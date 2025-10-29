from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from decimal import Decimal

from .models import Item
from .services import StockService
from .currency_service import CurrencyService


class StockCostViewSet(viewsets.ViewSet):
    """
    API para obter custos de estoque.
    """
    
    def list(self, request):
        """
        Retorna os custos de estoque com base na data e filtros.
        """
        # Parse date
        stock_date = request.query_params.get('stockDate', None)
        if stock_date:
            try:
                stock_date = datetime.strptime(stock_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"error": "Formato de data inválido. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            stock_date = datetime.now().date()
        
        # Get filters
        sku_filter = request.query_params.get('sku', '')
        description_filter = request.query_params.get('description', '')
        has_stock = request.query_params.get('hasStock', '') == 'true'
        active_only = request.query_params.get('active', '') == 'true'
        show_in_usd = request.query_params.get('showInUSD', '') == 'true'
        
        # Get ordering parameters
        ordering = request.query_params.get('ordering', '')
        
        # Get USD conversion rate if needed
        usd_rate = None
        if show_in_usd:
            usd_rate = CurrencyService.get_usd_rate(stock_date)
            if usd_rate is None:
                return Response(
                    {"error": "Não foi possível obter a cotação do dólar para a data especificada"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        # Query items with filters
        items_query = Item.objects.all()
        
        if sku_filter:
            items_query = items_query.filter(cod_sku__icontains=sku_filter)
            
        if description_filter:
            items_query = items_query.filter(descricao_item__icontains=description_filter)
            
        if active_only:
            items_query = items_query.filter(active=True)
        
        result = []
        
        for item in items_query:
            # Calculate stock quantity
            estoque_atual = StockService.calculate_stock_quantity(item, stock_date)
            
            # Apply stock filter
            if has_stock and estoque_atual <= 0:
                continue
            
            # Calculate costs using services
            custo_medio = StockService.calculate_average_cost(item, stock_date)
            custo_ultima_entrada = StockService.get_last_entry_cost(item, stock_date)
            total_cost = custo_medio * estoque_atual
            
            # Convert to USD if requested
            if show_in_usd and usd_rate:
                custo_medio_usd = CurrencyService.convert_brl_to_usd(Decimal(str(custo_medio)), stock_date)
                total_cost_usd = CurrencyService.convert_brl_to_usd(Decimal(str(total_cost)), stock_date)
                custo_ultima_entrada_usd = CurrencyService.convert_brl_to_usd(Decimal(str(custo_ultima_entrada)), stock_date) if custo_ultima_entrada else None
                
                item_data = {
                    'sku': item.cod_sku,
                    'description': item.descricao_item,
                    'quantity': float(estoque_atual),
                    'unityMeasure': item.unid_medida,
                    'unitCost': float(custo_medio_usd) if custo_medio_usd else float(custo_medio),
                    'totalCost': float(total_cost_usd) if total_cost_usd else float(total_cost),
                    'active': item.active,
                    'lastEntryCost': float(custo_ultima_entrada_usd) if custo_ultima_entrada_usd else None,
                    'currency': 'USD'
                }
            else:
                item_data = {
                    'sku': item.cod_sku,
                    'description': item.descricao_item,
                    'quantity': float(estoque_atual),
                    'unityMeasure': item.unid_medida,
                    'unitCost': float(custo_medio),
                    'totalCost': float(total_cost),
                    'active': item.active,
                    'lastEntryCost': float(custo_ultima_entrada) if custo_ultima_entrada else None,
                    'currency': 'BRL'
                }
            
            result.append(item_data)
        
        # Apply ordering if specified
        if ordering:
            def sort_key(item):
                key_values = []
                for field in ordering.split(','):
                    field = field.strip()
                    if field.startswith('-'):
                        # Descending order
                        field_name = field[1:]
                        if field_name == 'sku':
                            key_values.append(item.get('sku', ''))
                        elif field_name == 'description':
                            key_values.append(item.get('description', ''))
                        elif field_name == 'quantity':
                            key_values.append(item.get('quantity', 0))
                        elif field_name == 'unityMeasure':
                            key_values.append(item.get('unityMeasure', ''))
                        elif field_name == 'unitCost':
                            key_values.append(item.get('unitCost', 0))
                        elif field_name == 'totalCost':
                            key_values.append(item.get('totalCost', 0))
                        elif field_name == 'active':
                            key_values.append(item.get('active', False))
                        elif field_name == 'lastEntryCost':
                            key_values.append(item.get('lastEntryCost', 0))
                    else:
                        # Ascending order
                        if field == 'sku':
                            key_values.append(item.get('sku', ''))
                        elif field == 'description':
                            key_values.append(item.get('description', ''))
                        elif field == 'quantity':
                            key_values.append(item.get('quantity', 0))
                        elif field == 'unityMeasure':
                            key_values.append(item.get('unityMeasure', ''))
                        elif field == 'unitCost':
                            key_values.append(item.get('unitCost', 0))
                        elif field == 'totalCost':
                            key_values.append(item.get('totalCost', 0))
                        elif field == 'active':
                            key_values.append(item.get('active', False))
                        elif field == 'lastEntryCost':
                            key_values.append(item.get('lastEntryCost', 0))
                return key_values
            
            # Determine if we need reverse sorting based on the first field
            reverse_sort = ordering.split(',')[0].strip().startswith('-') if ordering else False
            result.sort(key=sort_key, reverse=reverse_sort)
        
        # Apply pagination
        page_size = int(request.query_params.get('page_size', 10))
        page = int(request.query_params.get('page', 1))
        
        total_count = len(result)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        paginated_results = result[start_index:end_index]
        
        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        
        return Response({
            'results': paginated_results,
            'count': total_count,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'next': page < total_pages,
            'previous': page > 1
        }) 