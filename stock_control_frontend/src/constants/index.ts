/**
 * Constantes da aplicação
 * 
 * Este arquivo centraliza todos os valores constantes usados na aplicação,
 * facilitando manutenção e evitando "magic numbers" espalhados pelo código.
 */

// ==============================================================================
// PAGINAÇÃO
// ==============================================================================

/**
 * Tamanho padrão de página para listagens
 */
export const DEFAULT_PAGE_SIZE = 10;

/**
 * Opções de tamanho de página disponíveis
 */
export const PAGE_SIZE_OPTIONS = [5, 10, 25, 50, 100] as const;

/**
 * Tamanho máximo de página permitido
 */
export const MAX_PAGE_SIZE = 100;

/**
 * Página inicial (primeira página)
 */
export const INITIAL_PAGE = 1;


// ==============================================================================
// FORMATAÇÃO
// ==============================================================================

/**
 * Locale para formatação de números e datas
 */
export const LOCALE = 'pt-BR';

/**
 * Moeda padrão
 */
export const CURRENCY = 'BRL';

/**
 * Formato de data padrão (DD/MM/YYYY)
 */
export const DATE_FORMAT = 'dd/MM/yyyy';

/**
 * Formato de data ISO (YYYY-MM-DD)
 */
export const ISO_DATE_FORMAT = 'yyyy-MM-dd';

/**
 * Formato de data e hora completo
 */
export const DATETIME_FORMAT = 'dd/MM/yyyy HH:mm:ss';


// ==============================================================================
// DEBOUNCE E DELAYS
// ==============================================================================

/**
 * Delay padrão para debounce em campos de busca (ms)
 */
export const SEARCH_DEBOUNCE_DELAY = 300;

/**
 * Delay para auto-save (ms)
 */
export const AUTOSAVE_DELAY = 1000;

/**
 * Delay para toast notifications (ms)
 */
export const TOAST_DURATION = 3000;

/**
 * Delay para tooltips (ms)
 */
export const TOOLTIP_DELAY = 500;


// ==============================================================================
// VALIDAÇÃO
// ==============================================================================

/**
 * Tamanho mínimo de senha
 */
export const MIN_PASSWORD_LENGTH = 8;

/**
 * Tamanho máximo de senha
 */
export const MAX_PASSWORD_LENGTH = 128;

/**
 * Tamanho máximo para código SKU
 */
export const MAX_SKU_LENGTH = 50;

/**
 * Tamanho máximo para descrição de item
 */
export const MAX_ITEM_DESCRIPTION_LENGTH = 1000;

/**
 * Tamanho máximo para nome de fornecedor
 */
export const MAX_SUPPLIER_NAME_LENGTH = 255;

/**
 * Quantidade mínima válida
 */
export const MIN_QUANTITY = 0.01;

/**
 * Valor unitário mínimo
 */
export const MIN_UNIT_COST = 0.01;


// ==============================================================================
// API E REQUISIÇÕES
// ==============================================================================

/**
 * Timeout padrão para requisições HTTP (ms)
 */
export const API_TIMEOUT = 30000;

/**
 * Número máximo de tentativas para requisições que falharam
 */
export const MAX_RETRY_ATTEMPTS = 3;

/**
 * Base URL da API (deve ser configurada via env)
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';


// ==============================================================================
// STORAGE KEYS
// ==============================================================================

/**
 * Chaves do localStorage
 */
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_PREFERENCES: 'user_preferences',
  ACCESSIBILITY_FONT_SIZE: 'accessibility_fontSize',
  ACCESSIBILITY_HIGH_CONTRAST: 'accessibility_highContrast',
  ACCESSIBILITY_REDUCED_MOTION: 'accessibility_reducedMotion',
  LAST_VISITED_PAGE: 'last_visited_page',
  FILTERS_STATE: 'filters_state',
} as const;


// ==============================================================================
// CORES E TEMAS
// ==============================================================================

/**
 * Cores do sistema (devem coincidir com CSS)
 */
export const COLORS = {
  PRIMARY: '#3b82f6',
  SECONDARY: '#64748b',
  SUCCESS: '#22c55e',
  WARNING: '#f59e0b',
  DANGER: '#ef4444',
  INFO: '#06b6d4',
  LIGHT: '#f8fafc',
  DARK: '#1e293b',
} as const;

/**
 * Variantes de botão disponíveis
 */
export const BUTTON_VARIANTS = ['primary', 'secondary', 'success', 'warning', 'danger', 'info'] as const;


// ==============================================================================
// ACESSIBILIDADE
// ==============================================================================

/**
 * Tamanhos de fonte disponíveis
 */
export const FONT_SIZES = {
  SMALL: 'small',
  NORMAL: 'normal',
  LARGE: 'large',
  EXTRA_LARGE: 'extra-large',
} as const;

/**
 * Multiplicadores de tamanho de fonte
 */
export const FONT_SIZE_MULTIPLIERS = {
  [FONT_SIZES.SMALL]: 0.875,
  [FONT_SIZES.NORMAL]: 1,
  [FONT_SIZES.LARGE]: 1.125,
  [FONT_SIZES.EXTRA_LARGE]: 1.25,
} as const;


// ==============================================================================
// TIPOS DE TRANSAÇÃO
// ==============================================================================

/**
 * Tipos de transação disponíveis
 */
export const TRANSACTION_TYPES = {
  ENTRADA: 'entrada',
  SAIDA: 'saida',
} as const;


// ==============================================================================
// STATUS DE CARREGAMENTO
// ==============================================================================

/**
 * Estados de carregamento possíveis
 */
export const LOADING_STATES = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
} as const;


// ==============================================================================
// MENSAGENS
// ==============================================================================

/**
 * Mensagens de erro comuns
 */
export const ERROR_MESSAGES = {
  GENERIC: 'Ocorreu um erro. Tente novamente.',
  NETWORK: 'Erro de conexão. Verifique sua internet.',
  UNAUTHORIZED: 'Você não tem permissão para esta ação.',
  NOT_FOUND: 'Recurso não encontrado.',
  VALIDATION: 'Dados inválidos. Verifique os campos.',
  SERVER: 'Erro no servidor. Tente novamente mais tarde.',
  TIMEOUT: 'Requisição excedeu o tempo limite.',
} as const;

/**
 * Mensagens de sucesso comuns
 */
export const SUCCESS_MESSAGES = {
  CREATED: 'Criado com sucesso!',
  UPDATED: 'Atualizado com sucesso!',
  DELETED: 'Deletado com sucesso!',
  SAVED: 'Salvo com sucesso!',
} as const;


// ==============================================================================
// REGEX PATTERNS
// ==============================================================================

/**
 * Padrões regex para validação
 */
export const REGEX_PATTERNS = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^\(?([0-9]{2})\)?[-. ]?([0-9]{4,5})[-. ]?([0-9]{4})$/,
  CPF: /^\d{3}\.\d{3}\.\d{3}-\d{2}$/,
  CNPJ: /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/,
  NUMBERS_ONLY: /^\d+$/,
  ALPHANUMERIC: /^[a-zA-Z0-9]+$/,
} as const;


// ==============================================================================
// ROTAS
// ==============================================================================

/**
 * Caminhos de rotas da aplicação
 */
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  ITEMS: '/itens',
  SUPPLIERS: '/fornecedores',
  TRANSACTIONS: '/transacoes',
  STOCK: '/estoque',
  STOCK_COSTS: '/custos-estoque',
  USERS: '/usuarios',
  PROFILE: '/perfil',
  SETTINGS: '/configuracoes',
  NOT_FOUND: '/404',
} as const;


// ==============================================================================
// EXPORTAÇÃO DE TIPOS
// ==============================================================================

/**
 * Tipo para tamanhos de página
 */
export type PageSize = typeof PAGE_SIZE_OPTIONS[number];

/**
 * Tipo para tamanhos de fonte
 */
export type FontSize = typeof FONT_SIZES[keyof typeof FONT_SIZES];

/**
 * Tipo para variantes de botão
 */
export type ButtonVariant = typeof BUTTON_VARIANTS[number];

/**
 * Tipo para tipos de transação
 */
export type TransactionType = typeof TRANSACTION_TYPES[keyof typeof TRANSACTION_TYPES];

/**
 * Tipo para estados de carregamento
 */
export type LoadingState = typeof LOADING_STATES[keyof typeof LOADING_STATES];

/**
 * Tipo para chaves de storage
 */
export type StorageKey = typeof STORAGE_KEYS[keyof typeof STORAGE_KEYS];


