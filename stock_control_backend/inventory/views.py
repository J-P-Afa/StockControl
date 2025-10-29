from decimal import Decimal
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Transacao, Item, Entrada, Saida, Fornecedor, Usuario, User
from .constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from .serializers import (
    TransacaoSerializer,
    ItemSerializer,
    EntradaSerializer,
    SaidaSerializer,
    FornecedorSerializer,
    UsuarioSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    UserDetailSerializer,
)
from .filters import ItemFilter, FornecedorFilter, TransacaoFilter, EntradaFilter, SaidaFilter, UsuarioFilter, UserFilter
from .services import StockService, TransactionService, UserService
from .currency_service import CurrencyService
from .utils import camelize_dict_keys


class StandardResultsSetPagination(PageNumberPagination):
    """Classe de paginação padrão para todos os ViewSets."""
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE


class PaginatedViewSet(viewsets.ModelViewSet):
    """ViewSet base com paginação padrão configurada."""
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]


class TransacaoViewSet(PaginatedViewSet):
    """
    ViewSet para listar, criar, atualizar e remover Transações.
    
    Otimização: usa select_related para evitar queries N+1 ao acessar
    cod_sku (Item) e cod_fornecedor (Fornecedor).
    """
    queryset = Transacao.objects.select_related('cod_sku', 'cod_fornecedor').all()
    serializer_class = TransacaoSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TransacaoFilter
    
    def create(self, request, *args, **kwargs):
        """
        Override create method to validate stock availability for saidas.
        """
        # Check if this is a transaction for a 'saida' by looking for 'is_saida' flag in request
        is_saida = request.data.get('is_saida', False)
        
        if is_saida:
            # This will be a saida transaction, we need to check stock availability
            try:
                cod_sku = request.data.get('cod_sku')
                quantidade = Decimal(request.data.get('quantidade', 0))
                
                if not cod_sku or quantidade <= 0:
                    return Response(
                        {"detail": "Dados inválidos para validação de estoque"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Use service to validate stock
                validation = TransactionService.validate_stock_availability(cod_sku, quantidade)
                
                if not validation['valid']:
                    return Response(
                        {"detail": validation['message']},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except Exception as e:
                return Response(
                    {"detail": f"Erro ao validar estoque: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Continue with normal creation
        return super().create(request, *args, **kwargs)


class ItemViewSet(PaginatedViewSet):
    """
    ViewSet para listar, criar, atualizar e remover Itens do estoque.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ItemFilter
    search_fields = ['cod_sku', 'descricao_item']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros extras
        show_only_active_items = self.request.query_params.get('show_only_active_items') == 'true'
        
        # Filtro por itens ativos
        if show_only_active_items:
            queryset = queryset.filter(active=True)
            
        return queryset

    @action(detail=True, methods=['get'], url_path='custo-medio')
    def custo_medio(self, request, pk=None):
        """
        Retorna o custo médio e custo da última entrada de um item.
        """
        try:
            item = self.get_object()
            
            # Use service to calculate costs
            custo_medio = StockService.calculate_average_cost(item)
            custo_ultima_entrada = StockService.get_last_entry_cost(item)
            
            # Round values
            custo_medio = round(custo_medio, 2)
            custo_ultima_entrada = round(custo_ultima_entrada, 2)
            
            return Response(camelize_dict_keys({
                'custo_medio': custo_medio, 
                'custo_ultima_entrada': custo_ultima_entrada
            }))
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StockViewSet(viewsets.ViewSet):
    """
    ViewSet para obter informações de estoque dos produtos.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        Retorna a lista de produtos com informações de estoque.
        """
        # Get query parameters
        stock_date_str = request.query_params.get('stockDate', None)
        item_sku = request.query_params.get('codSku', '')
        item_description = request.query_params.get('descricaoItem', '')
        show_only_stock_items = request.query_params.get('showOnlyStockItems') == 'true'
        show_only_active_items = request.query_params.get('showOnlyActiveItems') == 'true'
        ordering = request.query_params.get('ordering', '')
        
        # Parse date
        if stock_date_str:
            try:
                stock_date = datetime.strptime(stock_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"detail": "Data inválida. Use o formato YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            stock_date = datetime.now().date()
        
        # Use service to get stock items (ordenação incluída)
        result_items = StockService.get_stock_items(
            stock_date=stock_date,
            sku_filter=item_sku,
            description_filter=item_description,
            show_only_stock_items=show_only_stock_items,
            show_only_active_items=show_only_active_items,
            ordering=ordering
        )
        
        # Apply pagination
        page_size = int(request.query_params.get('page_size', 10))
        page = int(request.query_params.get('page', 1))
        
        total_count = len(result_items)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        paginated_results = result_items[start_index:end_index]
        
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


class EntradaViewSet(PaginatedViewSet):
    """
    ViewSet para gerenciar as entradas de produtos no estoque.
    
    Otimização: usa select_related para carregar transacao, usuario,
    e os relacionamentos da transacao (item e fornecedor) em uma única query.
    """
    queryset = Entrada.objects.select_related(
        'transacao',
        'transacao__cod_sku',
        'transacao__cod_fornecedor',
        'mat_usuario'
    ).all()
    serializer_class = EntradaSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EntradaFilter


class SaidaViewSet(PaginatedViewSet):
    """
    ViewSet para gerenciar as saídas (pedidos) do estoque.
    
    Otimização: usa select_related para carregar transacao, usuario,
    e os relacionamentos da transacao (item e fornecedor) em uma única query.
    """
    queryset = Saida.objects.select_related(
        'transacao',
        'transacao__cod_sku',
        'transacao__cod_fornecedor',
        'mat_usuario'
    ).all()
    serializer_class = SaidaSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = SaidaFilter
    
    def create(self, request, *args, **kwargs):
        """
        Cria uma nova saída com validação de estoque.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validação de estoque disponível
        transacao_id = serializer.validated_data['transacao'].id_transacao
        
        try:
            transacao = Transacao.objects.get(id_transacao=transacao_id)
            qtd_saida = transacao.quantidade
            cod_sku = transacao.cod_sku
            
            # Use service to validate stock
            validation = TransactionService.validate_stock_availability(cod_sku, qtd_saida)
            
            if not validation['valid']:
                return Response(
                    {"detail": validation['message']},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Transacao.DoesNotExist:
            return Response(
                {"detail": "Transação não encontrada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class FornecedorViewSet(PaginatedViewSet):
    """
    ViewSet para cadastrar e gerenciar os fornecedores.
    """
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = FornecedorFilter


class UsuarioViewSet(PaginatedViewSet):
    """
    ViewSet para gerenciar os usuários do sistema.
    """
    serializer_class = UsuarioSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = UsuarioFilter
    
    def get_queryset(self):
        return Usuario.objects.all().select_related('auth_user')


class UserViewSet(PaginatedViewSet):
    """
    ViewSet para gerenciar usuários do sistema usando o modelo User do Django.
    """
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = UserFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserDetailSerializer
    
    def get_queryset(self):
        return User.objects.all().prefetch_related('inventory_user')


class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Usuário criado com sucesso!",
                "user": UserDetailSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Return the current authenticated user with detailed information
    """
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user_inventory_info(request):
    """
    Return the current authenticated user's inventory usuario information.
    This endpoint specifically returns the mat_usuario needed for transactions.
    If no associated Usuario instance exists, one will be created.
    """
    try:
        # Use service to get or create inventory user
        usuario = UserService.get_or_create_inventory_user(request.user)
        
        # Return just the necessary information for transactions
        return Response({
            'id': usuario.mat_usuario,  # Return mat_usuario as id
            'nomeUsuario': usuario.nome_usuario
        })
    except Exception as e:
        return Response(
            {"detail": f"Error retrieving user inventory info: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unified_transactions(request):
    """
    Returns combined transaction data with related entry/exit, item, and user data in a single call.
    This optimizes frontend performance by reducing multiple API calls to one.
    """
    # Get query parameters
    date_from = request.query_params.get('dateFrom', None)
    date_to = request.query_params.get('dateTo', None)
    nota_fiscal = request.query_params.get('notaFiscal', None)
    sku = request.query_params.get('sku', None)
    description = request.query_params.get('description', None)
    show_in_usd = request.query_params.get('showInUSD', '') == 'true'
    ordering = request.query_params.get('ordering', '-cronology')
    
    # Get pagination parameters
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))
    
    # Get USD conversion rate if needed
    usd_rate = None
    if show_in_usd:
        # Use date_from as reference date, or today if not provided
        reference_date = None
        if date_from:
            try:
                reference_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        usd_rate = CurrencyService.get_usd_rate(reference_date)
        if usd_rate is None:
            return Response(
                {"error": "Não foi possível obter a cotação do dólar para a data especificada"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    # Use service to get unified transactions
    result = TransactionService.get_unified_transactions(
        date_from=date_from,
        date_to=date_to,
        nota_fiscal=nota_fiscal,
        sku=sku,
        description=description,
        show_in_usd=show_in_usd,
        usd_rate=usd_rate
    )
    
    # Apply ordering
    if ordering:
        # Convert ordering to work with our unified format
        if ordering.startswith('-'):
            reverse = True
            field = ordering[1:]
        else:
            reverse = False
            field = ordering
            
        # Map ordering fields
        if field == 'cronology':
            result.sort(key=lambda x: x['idTransacao'], reverse=reverse)
        elif field == 'date':
            result.sort(key=lambda x: x['date'], reverse=reverse)
        elif field == 'time':
            result.sort(key=lambda x: x['time'], reverse=reverse)
        elif field == 'sku':
            result.sort(key=lambda x: x['sku'], reverse=reverse)
        elif field == 'description':
            result.sort(key=lambda x: x['description'], reverse=reverse)
        elif field == 'quantity':
            result.sort(key=lambda x: x['quantity'], reverse=reverse)
        elif field == 'totalCost' or field == 'cost':
            result.sort(key=lambda x: x['totalCost'], reverse=reverse)
        elif field == 'notaFiscal':
            result.sort(key=lambda x: x.get('notaFiscal', ''), reverse=reverse)
        elif field == 'username':
            result.sort(key=lambda x: x.get('username', ''), reverse=reverse)
        elif field == 'transactionType':
            result.sort(key=lambda x: x['transactionType'], reverse=reverse)
    
    # Apply pagination
    total_count = len(result)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_results = result[start_index:end_index]
    
    # Calculate pagination info
    total_pages = (total_count + page_size - 1) // page_size
    
    return Response({
        'results': paginated_results,
        'count': total_count,
        'next': page < total_pages,
        'previous': page > 1
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recalculate_costs(request):
    """
    Recalcula os custos das transações subsequentes após uma modificação.
    """
    try:
        transaction_id = request.data.get('transactionId')
        sku = request.data.get('sku')
        
        if not transaction_id or not sku:
            return Response(
                {"detail": "transactionId e sku são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = TransactionService.recalculate_subsequent_costs(transaction_id, sku)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(
            {"detail": f"Erro ao recalcular custos: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_stock_operation(request):
    """
    Valida se uma operação manterá o estoque positivo.
    """
    try:
        sku = request.data.get('sku')
        operation_type = request.data.get('operationType')
        transaction_id = request.data.get('transactionId')
        new_quantity = request.data.get('newQuantity')
        
        if not sku or not operation_type:
            return Response(
                {"detail": "sku e operationType são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = TransactionService.validate_stock_after_operation(
            sku, operation_type, transaction_id, 
            Decimal(str(new_quantity)) if new_quantity else None
        )
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"detail": f"Erro na validação: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_transaction(request, transaction_id):
    """
    Deleta uma transação com validação de estoque e recálculo de custos.
    """
    try:
        result = TransactionService.delete_transaction_with_validation(transaction_id)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(
            {"detail": f"Erro ao excluir transação: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_transaction(request, transaction_id):
    """
    Atualiza uma transação com validação de estoque e recálculo de custos.
    """
    try:
        new_data = request.data
        result = TransactionService.update_transaction_with_validation(transaction_id, new_data)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(
            {"detail": f"Erro ao atualizar transação: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
