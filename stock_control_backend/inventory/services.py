"""
Serviços para lógica de negócio do sistema de inventário.

Este módulo contém a lógica de negócio separada das views,
facilitando a manutenção e testes.
"""

from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, F, Prefetch
from django.db.models.functions import Coalesce
from typing import List, Dict, Optional, Any

from .models import Item, Transacao, Entrada, Saida, Usuario
from .constants import (
    CONSUMPTION_CALCULATION_DAYS,
    CONSUMPTION_CALCULATION_MONTHS,
    ERROR_INSUFFICIENT_STOCK,
    INFO_NO_STOCK,
    INFO_NO_RECENT_CONSUMPTION,
    INFO_STOCK_AVAILABLE,
)
from .currency_service import CurrencyService


class StockService:
    """Serviço para operações relacionadas ao estoque."""
    
    @staticmethod
    def calculate_stock_quantity(item: Item, stock_date: Optional[date] = None) -> Decimal:
        """
        Calcula a quantidade em estoque de um item em uma data específica.
        
        Args:
            item: Item para calcular o estoque
            stock_date: Data para calcular o estoque (padrão: hoje)
            
        Returns:
            Decimal: Quantidade em estoque
        """
        if stock_date is None:
            stock_date = date.today()
            
        # Calcular entradas até a data
        entradas = Transacao.objects.filter(
            cod_sku=item,
            entradas__data_entrada__lte=stock_date
        ).aggregate(
            total=Coalesce(Sum('quantidade'), Decimal(0))
        )['total']
        
        # Calcular saídas até a data
        saidas = Transacao.objects.filter(
            cod_sku=item,
            saidas__data_saida__lte=stock_date
        ).aggregate(
            total=Coalesce(Sum('quantidade'), Decimal(0))
        )['total']
        
        return entradas - saidas

    @staticmethod
    def calculate_average_cost(item: Item, stock_date: Optional[date] = None) -> Decimal:
        """
        Calcula o custo médio de um item em uma data específica.
        
        Args:
            item: Item para calcular o custo
            stock_date: Data para calcular o custo (padrão: hoje)
            
        Returns:
            Decimal: Custo médio do item
        """
        if stock_date is None:
            stock_date = date.today()
            
        # Calcular valor total das entradas
        entradas_valor = Transacao.objects.filter(
            cod_sku=item,
            entradas__data_entrada__lte=stock_date
        ).aggregate(
            total=Coalesce(Sum(F('quantidade') * F('valor_unit')), Decimal(0))
        )['total']
        
        # Calcular valor total das saídas
        saidas_valor = Transacao.objects.filter(
            cod_sku=item,
            saidas__data_saida__lte=stock_date
        ).aggregate(
            total=Coalesce(Sum(F('quantidade') * F('valor_unit')), Decimal(0))
        )['total']
        
        # Calcular quantidade em estoque
        estoque_atual = StockService.calculate_stock_quantity(item, stock_date)
        
        if estoque_atual > 0:
            valor_estoque = entradas_valor - saidas_valor
            return valor_estoque / estoque_atual
        
        return Decimal(0)

    @staticmethod
    def get_last_entry_cost(item: Item, stock_date: Optional[date] = None) -> Decimal:
        """
        Obtém o custo da última entrada de um item.
        
        Args:
            item: Item para obter o custo
            stock_date: Data limite (padrão: hoje)
            
        Returns:
            Decimal: Custo da última entrada
        """
        if stock_date is None:
            stock_date = date.today()
            
        ultima_entrada = Transacao.objects.filter(
            cod_sku=item,
            entradas__data_entrada__lte=stock_date
        ).order_by('-id_transacao').first()
        
        return ultima_entrada.valor_unit if ultima_entrada else Decimal(0)

    @staticmethod
    def calculate_consumption_estimate(item: Item, stock_date: Optional[date] = None) -> str:
        """
        Calcula estimativa de tempo de consumo baseada nos últimos 3 meses.
        
        Args:
            item: Item para calcular a estimativa
            stock_date: Data base para cálculo (padrão: hoje)
            
        Returns:
            str: Estimativa de tempo de consumo
        """
        if stock_date is None:
            stock_date = date.today()
            
        # Calcular quantidade em estoque
        quantidade = StockService.calculate_stock_quantity(item, stock_date)
        
        if quantidade <= 0:
            return INFO_NO_STOCK
        
        # Calcular consumo dos últimos N meses (definido em constantes)
        months_ago = stock_date - relativedelta(months=CONSUMPTION_CALCULATION_MONTHS)
        
        saidas_recentes = Transacao.objects.filter(
            cod_sku=item,
            saidas__data_saida__gte=months_ago,
            saidas__data_saida__lte=stock_date
        ).aggregate(
            total=Coalesce(Sum('quantidade'), Decimal(0))
        )['total']
        
        # Calcular média diária usando período definido em constantes
        media_diaria = saidas_recentes / CONSUMPTION_CALCULATION_DAYS if saidas_recentes > 0 else 0
        
        if media_diaria <= 0:
            return INFO_NO_RECENT_CONSUMPTION
        
        # Calcular dias estimados
        dias_estimados = quantidade / media_diaria
        
        # Formatar estimativa
        if dias_estimados < 1:
            return "Menos de 1 dia"
        elif dias_estimados < 7:
            return f"{int(dias_estimados)} {'dia' if int(dias_estimados) == 1 else 'dias'}"
        elif dias_estimados < 30:
            semanas = dias_estimados / 7
            return f"{int(semanas)} {'semana' if int(semanas) == 1 else 'semanas'}"
        elif dias_estimados < 365:
            meses = dias_estimados / 30
            return f"{int(meses)} {'mês' if int(meses) == 1 else 'meses'}"
        else:
            anos = dias_estimados / 365
            return f"{int(anos)} {'ano' if int(anos) == 1 else 'anos'}"

    @staticmethod
    def sort_stock_items(items: List[Dict[str, Any]], ordering: str) -> List[Dict[str, Any]]:
        """
        Ordena lista de itens de estoque baseado no parâmetro de ordenação.
        
        Args:
            items: Lista de itens a ordenar
            ordering: String de ordenação (ex: 'codSku', '-quantity')
            
        Returns:
            List[Dict]: Lista ordenada
        """
        if not ordering:
            return items
        
        # Mapear campos para suas chaves no dicionário
        field_map = {
            'codSku': 'codSku',
            'descricaoItem': 'descricaoItem',
            'unidMedida': 'unidMedida',
            'active': 'active',
            'quantity': 'quantity',
            'estimatedConsumptionTime': 'estimatedConsumptionTime'
        }
        
        # Processar múltiplos campos de ordenação
        order_fields = [f.strip() for f in ordering.split(',')]
        
        def sort_key(item):
            values = []
            for field in order_fields:
                reverse = field.startswith('-')
                field_name = field[1:] if reverse else field
                
                if field_name in field_map:
                    value = item.get(field_map[field_name], '')
                    # Para ordenação reversa, inverter o valor
                    if reverse:
                        if isinstance(value, (int, float)):
                            value = -value
                        elif isinstance(value, str):
                            # Para strings, não podemos simplesmente negar
                            pass
                    values.append(value)
            return values
        
        # Determinar se precisa ordenação reversa (baseado no primeiro campo)
        reverse_sort = order_fields[0].strip().startswith('-') if order_fields else False
        
        return sorted(items, key=sort_key, reverse=reverse_sort)
    
    @staticmethod
    def get_stock_items(
        stock_date: Optional[date] = None,
        sku_filter: str = '',
        description_filter: str = '',
        show_only_stock_items: bool = False,
        show_only_active_items: bool = False,
        ordering: str = ''
    ) -> List[Dict[str, Any]]:
        """
        Obtém lista de itens com informações de estoque.
        
        Args:
            stock_date: Data para calcular estoque
            sku_filter: Filtro por código SKU
            description_filter: Filtro por descrição
            show_only_stock_items: Mostrar apenas itens com estoque
            show_only_active_items: Mostrar apenas itens ativos
            ordering: String de ordenação (ex: 'codSku', '-quantity')
            
        Returns:
            List[Dict]: Lista de itens com informações de estoque
        """
        if stock_date is None:
            stock_date = date.today()
        
        # Query base
        items_query = Item.objects.all()
        
        # Aplicar filtros
        if sku_filter:
            items_query = items_query.filter(cod_sku__icontains=sku_filter)
        
        if description_filter:
            items_query = items_query.filter(descricao_item__icontains=description_filter)
        
        if show_only_active_items:
            items_query = items_query.filter(active=True)
        
        result_items = []
        
        for item in items_query:
            try:
                # Calcular quantidade em estoque
                quantidade = StockService.calculate_stock_quantity(item, stock_date)
                
                # Pular itens sem estoque se filtro aplicado
                if show_only_stock_items and quantidade <= 0:
                    continue
                
                # Calcular estimativa de consumo
                estimated_consumption_time = StockService.calculate_consumption_estimate(item, stock_date)
                
                result_items.append({
                    'codSku': item.cod_sku,
                    'descricaoItem': item.descricao_item,
                    'unidMedida': item.unid_medida,
                    'active': item.active,
                    'quantity': float(quantidade),
                    'estimatedConsumptionTime': estimated_consumption_time
                })
            except Exception as e:
                # Log error but continue with next item
                print(f"Erro processando item {item.cod_sku}: {str(e)}")
                continue
        
        # Aplicar ordenação se especificada
        if ordering:
            result_items = StockService.sort_stock_items(result_items, ordering)
        
        return result_items


class TransactionService:
    """Serviço para operações relacionadas a transações."""
    
    @staticmethod
    def validate_stock_availability(cod_sku: str, quantidade: Decimal) -> Dict[str, Any]:
        """
        Valida se há estoque suficiente para uma saída.
        
        Args:
            cod_sku: Código SKU do item
            quantidade: Quantidade solicitada
            
        Returns:
            Dict: Resultado da validação com 'valid' e 'message'
        """
        try:
            # Calcular estoque atual
            entradas = Transacao.objects.filter(
                cod_sku=cod_sku,
                entradas__isnull=False
            ).aggregate(
                total=Coalesce(Sum('quantidade'), Decimal(0))
            )['total']
            
            saidas = Transacao.objects.filter(
                cod_sku=cod_sku,
                saidas__isnull=False
            ).aggregate(
                total=Coalesce(Sum('quantidade'), Decimal(0))
            )['total']
            
            estoque_atual = entradas - saidas
            
            if estoque_atual < quantidade:
                return {
                    'valid': False,
                    'message': ERROR_INSUFFICIENT_STOCK.format(
                        available=estoque_atual,
                        requested=quantidade
                    )
                }
            
            return {'valid': True, 'message': INFO_STOCK_AVAILABLE}
            
        except Item.DoesNotExist:
            return {
                'valid': False,
                'message': f"Item com SKU '{cod_sku}' não encontrado"
            }
        except (ValueError, TypeError) as e:
            return {
                'valid': False,
                'message': f"Dados inválidos para validação: {str(e)}"
            }
        except Exception as e:
            # Log inesperado mas não quebra a aplicação
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro inesperado ao validar estoque: {str(e)}", exc_info=True)
            return {
                'valid': False,
                'message': f"Erro ao validar estoque: {str(e)}"
            }

    @staticmethod
    def get_unified_transactions(
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        nota_fiscal: Optional[str] = None,
        sku: Optional[str] = None,
        description: Optional[str] = None,
        show_in_usd: bool = False,
        usd_rate: Optional[Decimal] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém transações unificadas (entradas e saídas) com dados relacionados.
        
        Args:
            date_from: Data inicial
            date_to: Data final
            nota_fiscal: Filtro por nota fiscal
            sku: Filtro por SKU
            description: Filtro por descrição
            show_in_usd: Se deve converter valores para USD
            usd_rate: Taxa de conversão USD/BRL
            
        Returns:
            List[Dict]: Lista de transações unificadas
        """
        # Otimização: usar prefetch_related para carregar objetos relacionados
        transacao_prefetch = Prefetch(
            'transacao', 
            queryset=Transacao.objects.select_related('cod_sku', 'cod_fornecedor')
        )
        
        # Query base para entradas
        entradas_qs = Entrada.objects.select_related('mat_usuario').prefetch_related(transacao_prefetch)
        
        # Query base para saídas
        saidas_qs = Saida.objects.select_related('mat_usuario').prefetch_related(transacao_prefetch)
        
        # Aplicar filtros de data
        if date_from:
            entradas_qs = entradas_qs.filter(data_entrada__gte=date_from)
            saidas_qs = saidas_qs.filter(data_saida__gte=date_from)
        if date_to:
            entradas_qs = entradas_qs.filter(data_entrada__lte=date_to)
            saidas_qs = saidas_qs.filter(data_saida__lte=date_to)
        
        # Aplicar filtro por nota fiscal (apenas entradas)
        if nota_fiscal:
            entradas_qs = entradas_qs.filter(transacao__cod_nf=nota_fiscal)
            saidas_qs = saidas_qs.none()
        
        # Aplicar filtro por SKU
        if sku:
            entradas_qs = entradas_qs.filter(transacao__cod_sku=sku)
            saidas_qs = saidas_qs.filter(transacao__cod_sku=sku)
        
        # Aplicar filtro por descrição
        if description:
            entradas_qs = entradas_qs.filter(transacao__cod_sku__descricao_item__icontains=description)
            saidas_qs = saidas_qs.filter(transacao__cod_sku__descricao_item__icontains=description)
        
        # Ordenar para consistência
        entradas_qs = entradas_qs.order_by('-data_entrada', '-hora_entrada')
        saidas_qs = saidas_qs.order_by('-data_saida', '-hora_saida')
        
        # Buscar dados
        entradas_list = list(entradas_qs)
        saidas_list = list(saidas_qs)
        
        result = []
        
        # Processar entradas
        for entrada in entradas_list:
            transaction = entrada.transacao
            item = transaction.cod_sku
            usuario = entrada.mat_usuario
            
            # Calcular valores
            unit_cost = float(transaction.valor_unit)
            total_cost = float(transaction.quantidade * transaction.valor_unit)
            
            # Converter para USD se solicitado
            if show_in_usd and usd_rate:
                unit_cost_usd = CurrencyService.convert_brl_to_usd(Decimal(str(unit_cost)), entrada.data_entrada)
                total_cost_usd = CurrencyService.convert_brl_to_usd(Decimal(str(total_cost)), entrada.data_entrada)
                
                unit_cost = float(unit_cost_usd) if unit_cost_usd else unit_cost
                total_cost = float(total_cost_usd) if total_cost_usd else total_cost
            
            result.append({
                'id': f'entrada-{entrada.cod_entrada}',
                'idTransacao': transaction.id_transacao,
                'transactionType': 'entrada',
                'date': entrada.data_entrada.isoformat(),
                'time': entrada.hora_entrada.isoformat(),
                'sku': item.cod_sku,
                'description': item.descricao_item,
                'quantity': float(transaction.quantidade),
                'unityMeasure': item.unid_medida,
                'unitCost': unit_cost,
                'totalCost': total_cost,
                'notaFiscal': transaction.cod_nf,
                'username': usuario.nome_usuario if usuario else 'N/A',
                'currency': 'USD' if show_in_usd else 'BRL'
            })
        
        # Processar saídas
        for saida in saidas_list:
            transaction = saida.transacao
            item = transaction.cod_sku
            usuario = saida.mat_usuario
            
            # Calcular valores
            unit_cost = float(transaction.valor_unit)
            total_cost = float(transaction.quantidade * transaction.valor_unit)
            
            # Converter para USD se solicitado
            if show_in_usd and usd_rate:
                unit_cost_usd = CurrencyService.convert_brl_to_usd(Decimal(str(unit_cost)), saida.data_saida)
                total_cost_usd = CurrencyService.convert_brl_to_usd(Decimal(str(total_cost)), saida.data_saida)
                
                unit_cost = float(unit_cost_usd) if unit_cost_usd else unit_cost
                total_cost = float(total_cost_usd) if total_cost_usd else total_cost
            
            result.append({
                'id': f'saida-{saida.cod_pedido}',
                'idTransacao': transaction.id_transacao,
                'transactionType': 'saida',
                'date': saida.data_saida.isoformat(),
                'time': saida.hora_saida.isoformat(),
                'sku': item.cod_sku,
                'description': item.descricao_item,
                'quantity': float(transaction.quantidade),
                'unityMeasure': item.unid_medida,
                'unitCost': unit_cost,
                'totalCost': total_cost,
                'username': usuario.nome_usuario if usuario else 'N/A',
                'currency': 'USD' if show_in_usd else 'BRL'
            })
        
        return result


class UserService:
    """Serviço para operações relacionadas a usuários."""
    
    @staticmethod
    def get_or_create_inventory_user(user) -> Usuario:
        """
        Obtém ou cria um usuário de inventário para um usuário Django.
        
        Args:
            user: Usuário Django
            
        Returns:
            Usuario: Usuário de inventário
        """
        try:
            # Verificar se o usuário já tem um perfil de inventário
            if hasattr(user, 'inventory_user') and user.inventory_user:
                return user.inventory_user
            
            # Criar novo usuário de inventário
            last_usuario = Usuario.objects.order_by('-mat_usuario').first()
            new_mat_usuario = 1 if not last_usuario else last_usuario.mat_usuario + 1
            
            usuario = Usuario.objects.create(
                mat_usuario=new_mat_usuario,
                nome_usuario=user.get_full_name() or user.username,
                auth_user=user
            )
            
            return usuario
            
        except Usuario.DoesNotExist:
            # Este except nunca deveria ser chamado aqui, mas mantido por segurança
            raise Exception("Erro ao buscar último usuário")
        except ValueError as e:
            raise ValueError(f"Dados inválidos para criar usuário: {str(e)}")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro inesperado ao criar usuário de inventário: {str(e)}", exc_info=True)
            raise Exception(f"Erro ao criar usuário de inventário: {str(e)}")

    @staticmethod
    def _get_all_transactions_for_sku(sku: str) -> List[Dict[str, Any]]:
        """
        Busca e organiza todas as transações para um SKU específico.
        
        Args:
            sku: Código SKU do item
            
        Returns:
            List[Dict]: Lista de transações ordenadas por ID
        """
        # Buscar todas as transações para este SKU ordenadas por data
        entradas = Transacao.objects.filter(
            cod_sku=sku,
            entradas__isnull=False
        ).order_by('id_transacao')
        
        saidas = Transacao.objects.filter(
            cod_sku=sku,
            saidas__isnull=False
        ).order_by('id_transacao')
        
        # Combinar e ordenar todas as transações
        all_transactions = []
        for entrada in entradas:
            all_transactions.append({
                'id': entrada.id_transacao,
                'type': 'entrada',
                'quantity': entrada.quantidade,
                'unit_cost': entrada.valor_unit,
                'date': entrada.entradas.first().data_entrada
            })
        
        for saida in saidas:
            all_transactions.append({
                'id': saida.id_transacao,
                'type': 'saida',
                'quantity': saida.quantidade,
                'unit_cost': saida.valor_unit,
                'date': saida.saidas.first().data_saida
            })
        
        # Ordenar por ID (que representa ordem cronológica)
        all_transactions.sort(key=lambda x: x['id'])
        
        return all_transactions
    
    @staticmethod
    def _calculate_stock_until_transaction(
        transactions: List[Dict[str, Any]], 
        transaction_id: int
    ) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        """
        Calcula estoque e valores até uma transação específica.
        
        Args:
            transactions: Lista de transações
            transaction_id: ID da transação limite
            
        Returns:
            tuple: (entrada_qtde, entrada_valor, saida_qtde, saida_valor)
        """
        entrada_qtde = Decimal(0)
        entrada_valor = Decimal(0)
        saida_qtde = Decimal(0)
        saida_valor = Decimal(0)
        
        for tx in transactions:
            if tx['id'] <= transaction_id:
                if tx['type'] == 'entrada':
                    entrada_qtde += tx['quantity']
                    entrada_valor += tx['quantity'] * tx['unit_cost']
                else:
                    saida_qtde += tx['quantity']
                    saida_valor += tx['quantity'] * tx['unit_cost']
        
        return entrada_qtde, entrada_valor, saida_qtde, saida_valor
    
    @staticmethod
    def _update_subsequent_exit_costs(
        transactions: List[Dict[str, Any]], 
        transaction_id: int,
        entrada_qtde: Decimal,
        entrada_valor: Decimal,
        saida_qtde: Decimal,
        saida_valor: Decimal
    ) -> int:
        """
        Atualiza os custos das saídas subsequentes.
        
        Args:
            transactions: Lista de transações
            transaction_id: ID da transação modificada
            entrada_qtde: Quantidade de entradas acumulada
            entrada_valor: Valor de entradas acumulado
            saida_qtde: Quantidade de saídas acumulada
            saida_valor: Valor de saídas acumulado
            
        Returns:
            int: Número de transações atualizadas
        """
        updated_count = 0
        
        for tx in transactions:
            if tx['id'] > transaction_id:
                if tx['type'] == 'entrada':
                    entrada_qtde += tx['quantity']
                    entrada_valor += tx['quantity'] * tx['unit_cost']
                else:
                    # Calcular novo custo médio
                    estoque_atual = entrada_qtde - saida_qtde
                    valor_estoque_atual = entrada_valor - saida_valor
                    
                    if estoque_atual > 0:
                        novo_custo_medio = valor_estoque_atual / estoque_atual
                    else:
                        novo_custo_medio = Decimal(0)
                    
                    # Atualizar a transação
                    transacao = Transacao.objects.get(id_transacao=tx['id'])
                    transacao.valor_unit = round(novo_custo_medio, 2)
                    transacao.save()
                    
                    updated_count += 1
                    
                    # Atualizar contadores
                    saida_qtde += tx['quantity']
                    saida_valor += tx['quantity'] * novo_custo_medio
        
        return updated_count
    
    @staticmethod
    def recalculate_subsequent_costs(transaction_id: int, sku: str) -> Dict[str, Any]:
        """
        Recalcula os custos das saídas subsequentes após uma modificação.
        
        Args:
            transaction_id: ID da transação modificada
            sku: Código SKU do item
            
        Returns:
            Dict: Resultado da operação
        """
        try:
            # Buscar todas as transações
            all_transactions = TransactionService._get_all_transactions_for_sku(sku)
            
            # Calcular estoque e valor até o ponto de modificação
            entrada_qtde, entrada_valor, saida_qtde, saida_valor = \
                TransactionService._calculate_stock_until_transaction(all_transactions, transaction_id)
            
            # Recalcular custos das transações subsequentes
            updated_count = TransactionService._update_subsequent_exit_costs(
                all_transactions, transaction_id,
                entrada_qtde, entrada_valor, saida_qtde, saida_valor
            )
            
            return {
                'success': True,
                'updated_transactions': updated_count,
                'message': f'Recalculados custos de {updated_count} transações subsequentes'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Erro ao recalcular custos: {str(e)}'
            }

    @staticmethod
    def _simulate_stock_after_operation(
        transactions: List[Dict[str, Any]],
        operation_type: str,
        transaction_id: Optional[int],
        new_quantity: Optional[Decimal]
    ) -> tuple[bool, Decimal, Optional[int]]:
        """
        Simula o efeito de uma operação no estoque.
        
        Args:
            transactions: Lista de transações
            operation_type: Tipo de operação ('delete' ou 'edit')
            transaction_id: ID da transação
            new_quantity: Nova quantidade (para edit)
            
        Returns:
            tuple: (is_valid, final_stock, failed_transaction_id)
        """
        current_stock = Decimal(0)
        
        for tx in transactions:
            # Pular a transação que estamos excluindo
            if operation_type == 'delete' and tx['id'] == transaction_id:
                continue
            
            # Aplicar a nova quantidade para a transação que estamos editando
            quantity = tx['quantity']
            if operation_type == 'edit' and tx['id'] == transaction_id and new_quantity is not None:
                quantity = new_quantity
            
            # Atualizar o estoque simulado
            if tx['type'] == 'entrada':
                current_stock += quantity
            else:
                current_stock -= quantity
            
            # Verificar se o estoque ficou negativo
            if current_stock < 0:
                return False, current_stock, tx['id']
        
        return True, current_stock, None
    
    @staticmethod
    def validate_stock_after_operation(
        sku: str, 
        operation_type: str, 
        transaction_id: Optional[int] = None,
        new_quantity: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Valida se uma operação manterá o estoque positivo.
        
        Args:
            sku: Código SKU do item
            operation_type: Tipo de operação ('delete' ou 'edit')
            transaction_id: ID da transação (para edit)
            new_quantity: Nova quantidade (para edit)
            
        Returns:
            Dict: Resultado da validação
        """
        try:
            # Buscar todas as transações
            all_transactions = TransactionService._get_all_transactions_for_sku(sku)
            
            # Simular o efeito no estoque
            is_valid, final_stock, failed_tx_id = TransactionService._simulate_stock_after_operation(
                all_transactions, operation_type, transaction_id, new_quantity
            )
            
            if not is_valid:
                return {
                    'valid': False,
                    'message': f'Operação resultaria em estoque negativo ({final_stock}) após a transação {failed_tx_id}',
                    'stock_at_failure': float(final_stock)
                }
            
            return {
                'valid': True,
                'message': 'Operação válida - estoque permanecerá positivo',
                'final_stock': float(final_stock)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'message': f'Erro na validação: {str(e)}'
            }

    @staticmethod
    def delete_transaction_with_validation(transaction_id: str) -> Dict[str, Any]:
        """
        Deleta uma transação com validação de estoque e recálculo de custos.
        
        Args:
            transaction_id: ID da transação no formato 'tipo-id' (ex: 'entrada-123')
            
        Returns:
            Dict: Resultado da operação
        """
        try:
            transaction_type, id_str = transaction_id.split('-')
            transaction_db_id = int(id_str)
            
            if transaction_type == 'entrada':
                # Buscar a entrada
                entrada = Entrada.objects.get(cod_entrada=transaction_db_id)
                transacao = entrada.transacao
                sku = transacao.cod_sku.cod_sku
                
                # Validar se a exclusão não deixará estoque negativo
                validation = TransactionService.validate_stock_after_operation(
                    sku, 'delete', transacao.id_transacao
                )
                
                if not validation['valid']:
                    return {
                        'success': False,
                        'message': validation['message']
                    }
                
                # Excluir entrada e transação
                entrada.delete()
                transacao.delete()
                
                # Recalcular custos das saídas subsequentes
                TransactionService.recalculate_subsequent_costs(
                    transacao.id_transacao, sku
                )
                
            elif transaction_type == 'saida':
                # Buscar a saída
                saida = Saida.objects.get(cod_pedido=transaction_db_id)
                transacao = saida.transacao
                
                # Excluir saída e transação
                saida.delete()
                transacao.delete()
                
            else:
                return {
                    'success': False,
                    'message': f'Tipo de transação desconhecido: {transaction_type}'
                }
            
            return {
                'success': True,
                'message': f'Transação {transaction_id} excluída com sucesso'
            }
            
        except Entrada.DoesNotExist:
            return {
                'success': False,
                'error': 'not_found',
                'message': f'Entrada {transaction_id} não encontrada'
            }
        except Saida.DoesNotExist:
            return {
                'success': False,
                'error': 'not_found',
                'message': f'Saída {transaction_id} não encontrada'
            }
        except ValueError as e:
            return {
                'success': False,
                'error': 'invalid_format',
                'message': f'Formato de ID inválido: {str(e)}'
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro inesperado ao excluir transação: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'unexpected',
                'message': f'Erro ao excluir transação: {str(e)}'
            }

    @staticmethod
    def _update_entrada_transaction(
        entrada: 'Entrada',
        transacao: 'Transacao',
        new_data: Dict[str, Any]
    ) -> None:
        """
        Atualiza os dados de uma transação de entrada.
        
        Args:
            entrada: Objeto Entrada
            transacao: Objeto Transacao
            new_data: Novos dados da transação
        """
        if 'quantity' in new_data:
            transacao.quantidade = Decimal(str(new_data['quantity']))
        if 'unitCost' in new_data:
            transacao.valor_unit = Decimal(str(new_data['unitCost']))
        if 'codNf' in new_data:
            transacao.cod_nf = new_data['codNf']
        if 'supplierId' in new_data:
            from .models import Fornecedor
            transacao.cod_fornecedor = Fornecedor.objects.get(cod_fornecedor=new_data['supplierId'])
        
        transacao.save()
    
    @staticmethod
    def _update_saida_transaction(
        saida: 'Saida',
        transacao: 'Transacao',
        new_data: Dict[str, Any]
    ) -> None:
        """
        Atualiza os dados de uma transação de saída.
        
        Args:
            saida: Objeto Saida
            transacao: Objeto Transacao
            new_data: Novos dados da transação
        """
        if 'quantity' in new_data:
            transacao.quantidade = Decimal(str(new_data['quantity']))
        if 'unitCost' in new_data:
            transacao.valor_unit = Decimal(str(new_data['unitCost']))
        
        transacao.save()
    
    @staticmethod
    def update_transaction_with_validation(
        transaction_id: str, 
        new_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualiza uma transação com validação de estoque e recálculo de custos.
        
        Args:
            transaction_id: ID da transação no formato 'tipo-id'
            new_data: Novos dados da transação
            
        Returns:
            Dict: Resultado da operação
        """
        try:
            transaction_type, id_str = transaction_id.split('-')
            transaction_db_id = int(id_str)
            
            if transaction_type == 'entrada':
                entrada = Entrada.objects.get(cod_entrada=transaction_db_id)
                transacao = entrada.transacao
                sku = transacao.cod_sku.cod_sku
                
                # Validar se a modificação não deixará estoque negativo
                validation = TransactionService.validate_stock_after_operation(
                    sku, 'edit', transacao.id_transacao, 
                    Decimal(str(new_data.get('quantity', transacao.quantidade)))
                )
                
                if not validation['valid']:
                    return {'success': False, 'message': validation['message']}
                
                # Atualizar transação
                TransactionService._update_entrada_transaction(entrada, transacao, new_data)
                
                # Recalcular custos das saídas subsequentes
                TransactionService.recalculate_subsequent_costs(transacao.id_transacao, sku)
                
            elif transaction_type == 'saida':
                saida = Saida.objects.get(cod_pedido=transaction_db_id)
                transacao = saida.transacao
                sku = transacao.cod_sku.cod_sku
                
                # Validar se a modificação não deixará estoque negativo
                validation = TransactionService.validate_stock_after_operation(
                    sku, 'edit', transacao.id_transacao,
                    Decimal(str(new_data.get('quantity', transacao.quantidade)))
                )
                
                if not validation['valid']:
                    return {'success': False, 'message': validation['message']}
                
                # Atualizar transação
                TransactionService._update_saida_transaction(saida, transacao, new_data)
                
            else:
                return {
                    'success': False,
                    'message': f'Tipo de transação desconhecido: {transaction_type}'
                }
            
            return {
                'success': True,
                'message': f'Transação {transaction_id} atualizada com sucesso'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Erro ao atualizar transação: {str(e)}'
            }
