"""
Constantes do sistema de inventário.

Este módulo centraliza todos os valores constantes usados no sistema,
facilitando manutenção e evitando "magic numbers" espalhados pelo código.
"""

# ==============================================================================
# PAGINAÇÃO
# ==============================================================================

# Tamanho padrão de página para listagens
DEFAULT_PAGE_SIZE = 10

# Tamanhos de página permitidos
ALLOWED_PAGE_SIZES = [5, 10, 25, 50, 100]

# Tamanho máximo de página
MAX_PAGE_SIZE = 100


# ==============================================================================
# CÁLCULO DE ESTOQUE
# ==============================================================================

# Período em dias usado para calcular consumo médio
CONSUMPTION_CALCULATION_DAYS = 90

# Número de meses para cálculo de consumo médio
CONSUMPTION_CALCULATION_MONTHS = 3


# ==============================================================================
# LIMITES DE DADOS
# ==============================================================================

# Tamanho máximo para código SKU
MAX_SKU_LENGTH = 50

# Tamanho máximo para nome de fornecedor
MAX_SUPPLIER_NAME_LENGTH = 255

# Tamanho máximo para descrição de item
MAX_ITEM_DESCRIPTION_LENGTH = 1000

# Tamanho máximo para código de nota fiscal
MAX_NF_CODE_LENGTH = 50


# ==============================================================================
# VALORES DECIMAIS
# ==============================================================================

# Precisão para valores monetários
CURRENCY_MAX_DIGITS = 12
CURRENCY_DECIMAL_PLACES = 2

# Precisão para quantidades
QUANTITY_MAX_DIGITS = 20
QUANTITY_DECIMAL_PLACES = 2


# ==============================================================================
# TEMPO DE CONSUMO
# ==============================================================================

# Limites para categorização de tempo de consumo
CONSUMPTION_LESS_THAN_DAY = 1  # dias
CONSUMPTION_LESS_THAN_WEEK = 7  # dias
CONSUMPTION_LESS_THAN_MONTH = 30  # dias
CONSUMPTION_LESS_THAN_YEAR = 365  # dias


# ==============================================================================
# MENSAGENS DO SISTEMA
# ==============================================================================

# Mensagens de erro comuns
ERROR_INSUFFICIENT_STOCK = "Estoque insuficiente. Disponível: {available}, Solicitado: {requested}"
ERROR_INVALID_STOCK_DATA = "Dados inválidos para validação de estoque"
ERROR_TRANSACTION_NOT_FOUND = "Transação não encontrada"
ERROR_ITEM_NOT_FOUND = "Item não encontrado"
ERROR_SUPPLIER_NOT_FOUND = "Fornecedor não encontrado"
ERROR_USER_NOT_FOUND = "Usuário não encontrado"

# Mensagens de sucesso
SUCCESS_TRANSACTION_CREATED = "Transação criada com sucesso"
SUCCESS_TRANSACTION_UPDATED = "Transação atualizada com sucesso"
SUCCESS_TRANSACTION_DELETED = "Transação deletada com sucesso"

# Mensagens informativas
INFO_NO_STOCK = "Sem estoque"
INFO_NO_RECENT_CONSUMPTION = "Sem consumo recente"
INFO_STOCK_AVAILABLE = "Estoque disponível"


# ==============================================================================
# LOGGING
# ==============================================================================

# Níveis de log
LOG_LEVEL_DEBUG = 'DEBUG'
LOG_LEVEL_INFO = 'INFO'
LOG_LEVEL_WARNING = 'WARNING'
LOG_LEVEL_ERROR = 'ERROR'
LOG_LEVEL_CRITICAL = 'CRITICAL'


# ==============================================================================
# CACHE (para uso futuro)
# ==============================================================================

# Tempo de cache em segundos
CACHE_TIMEOUT_SHORT = 60  # 1 minuto
CACHE_TIMEOUT_MEDIUM = 300  # 5 minutos
CACHE_TIMEOUT_LONG = 3600  # 1 hora

# Prefixos de chaves de cache
CACHE_KEY_STOCK = 'stock'
CACHE_KEY_ITEM = 'item'
CACHE_KEY_COST = 'cost'
CACHE_KEY_TRANSACTION = 'transaction'


# ==============================================================================
# PERMISSÕES
# ==============================================================================

# Tipos de permissão
PERMISSION_VIEW = 'view'
PERMISSION_ADD = 'add'
PERMISSION_CHANGE = 'change'
PERMISSION_DELETE = 'delete'


# ==============================================================================
# TIPOS DE TRANSAÇÃO
# ==============================================================================

TRANSACTION_TYPE_ENTRADA = 'entrada'
TRANSACTION_TYPE_SAIDA = 'saida'


