import api from '@/types/api'
import type { Paginated } from '@/types/api'
import { getCurrentISODate, safeFormatBrazilianDateToISO } from '@/utils/date'

// Simple cache implementation
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  key: string;
}

class TransactionCache {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private cacheLifetime: number = 30000; // 30 seconds default cache lifetime
  
  // Generate a cache key from params
  generateKey(endpoint: string, params?: any): string {
    return `${endpoint}|${params ? JSON.stringify(params) : ''}`;
  }
  
  // Get value from cache
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) return null;
    
    // Check if entry has expired
    if (Date.now() - entry.timestamp > this.cacheLifetime) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data as T;
  }
  
  // Store value in cache
  set<T>(key: string, data: T): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      key
    });
  }
  
  // Clear cache
  clear(): void {
    this.cache.clear();
  }
  
  // Clear cache for specific endpoint
  clearEndpoint(endpoint: string): void {
    for (const [key, entry] of this.cache.entries()) {
      if (key.startsWith(endpoint)) {
        this.cache.delete(key);
      }
    }
  }
}

// Create a single cache instance
const transactionCache = new TransactionCache();

// Interfaces para objetos camelCase (resposta e envio da API)
export interface Transacao {
  idTransacao?: number
  codNf?: string
  codSku: string
  quantidade: number
  valorUnit: string
  codFornecedor?: number
  is_saida?: boolean  // Flag to indicate this is for a saida transaction (for stock validation)
}

export interface Entrada {
  codEntrada?: number
  transacao: number
  matUsuario: number
  dataEntrada: string
  horaEntrada: string
}

export interface Saida {
  codPedido?: number
  transacao: number
  matUsuario: number
  dataSaida: string
  horaSaida: string
}

// Interface para informações do usuário de inventário
export interface InventoryUserInfo {
  id: number;
  nomeUsuario: string;
}

// Interface para as transações formatadas para a tabela
export interface FormattedTransaction {
  id: string;
  idTransacao: number;
  transactionType: 'entrada' | 'saida';
  date: string;
  time: string;
  sku: string;
  description: string;
  quantity: number;
  unityMeasure: string;
  unitCost: number;
  totalCost: number;
  notaFiscal?: string;
  username?: string;
  currency?: string;
}

// Interface para parâmetros de busca
export interface TransactionSearchParams {
  sku?: string;
  description?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  notaFiscal?: string;
  showInUSD?: boolean;
  ordering?: string;
  page_size?: number;
}

class TransactionService {
  async getTransacoes(page = 1): Promise<Paginated<Transacao>> {
    const { data } = await api.get(`/api/v1/transacoes/`)
    return data
  }

  async createTransacao(t: Omit<Transacao, 'idTransacao'>): Promise<Transacao> {
    t.valorUnit = parseFloat(parseFloat(t.valorUnit).toFixed(2)).toString();
    console.log('Sending transacao payload:', t);
    
    const { data } = await api.post('/api/v1/transacoes/', t)
    
    // Clear cache after creating a transaction
    transactionCache.clearEndpoint('unified-transactions');
    
    return data
  }

  async getEntradas(page = 1, params?: { dataEntradaAfter?: string; dataEntradaBefore?: string; codNf?: string; codSku?: string }): Promise<Paginated<Entrada>> {
    let url = `/api/v1/entradas/`;
    
    // Add all parameters that are defined
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) {
          url += `&${key}=${encodeURIComponent(value)}`;
        }
      });
    }
    
    console.log('getEntradas: Making API call with URL:', url);
    console.log('getEntradas: Params:', params);
    
    const { data } = await api.get(url);
    console.log('getEntradas: Response:', data);
    
    return data;
  }

  async createEntrada(transacaoId: number, matUsuario: number): Promise<Entrada> {
    const dataEntrada = getCurrentISODate();
    const horaEntrada = new Date().toISOString().slice(11, 19);
    
    // Enviar diretamente em camelCase
    const entrada: Entrada = {
      transacao: transacaoId,
      matUsuario: matUsuario,
      dataEntrada: dataEntrada,
      horaEntrada: horaEntrada,
    }
    console.log('Sending entrada payload:', entrada);
    const { data } = await api.post('/api/v1/entradas/', entrada)
    
    // Clear cache after creating an entrada
    transactionCache.clearEndpoint('unified-transactions');
    
    return data
  }

  async getSaidas(page = 1, params?: { dataSaidaAfter?: string; dataSaidaBefore?: string; codSku?: string }): Promise<Paginated<Saida>> {
    let url = `/api/v1/saidas/`;
    
    // Add all parameters that are defined
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) {
          url += `&${key}=${encodeURIComponent(value)}`;
        }
      });
    }
    
    console.log('getSaidas: Making API call with URL:', url);
    console.log('getSaidas: Params:', params);
    
    const { data } = await api.get(url);
    console.log('getSaidas: Response:', data);
    
    return data;
  }

  async createSaida(transacaoId: number, matUsuario: number): Promise<Saida> {
    const dataSaida = getCurrentISODate();
    const horaSaida = new Date().toISOString().slice(11, 19);
    
    // Enviar diretamente em camelCase
    const saida: Saida = {
      transacao: transacaoId,
      matUsuario: matUsuario,
      dataSaida: dataSaida,
      horaSaida: horaSaida
    };
    
    console.log('Sending saida payload:', JSON.stringify(saida, null, 2));
    
    try {
      const { data } = await api.post('/api/v1/saidas/', saida);
      console.log('Saida response:', data);
      
      // Clear cache after creating a saida
      transactionCache.clearEndpoint('unified-transactions');
      
      return data;
    } catch (error: any) {
      console.error('Error creating saida:', error.response?.data || error.message);
      throw error;
    }
  }

  async getCurrentUserInventoryInfo(): Promise<InventoryUserInfo> {
    const { data } = await api.get('/api/v1/current-user-inventory-info/');
    console.log('Raw user inventory info response:', data);
    
    return data;
  }

  async createEntradaTransaction(
    codSku: string,
    quantidade: number,
    valorUnit: string,
    matUsuario: number,
    codNf: string,
    codFornecedor: number
  ): Promise<Entrada> {
    // Create Transacao first
    const transacao = await this.createTransacao({
      codNf: codNf,
      codSku,
      quantidade,
      valorUnit,
      codFornecedor,
    });
    
    // Then create Entrada
    return this.createEntrada(transacao.idTransacao!, matUsuario);
  }

  async createSaidaTransaction(
    codSku: string,
    quantidade: number,
    valorUnit: string,
    matUsuario: number
  ): Promise<Saida> {
    console.log('Creating saida transaction for SKU:', codSku);
    
    try {
      // Create Transacao first (without codNf and codFornecedor)
      // Pass is_saida flag to signal this is a transaction for a saida (for backend validation)
      const transacao = await this.createTransacao({
        codSku,
        quantidade,
        valorUnit,
        is_saida: true  // This flag tells the backend to validate stock availability
      });
      
      console.log('Transaction created with ID:', transacao.idTransacao);
      
      // Then create Saida
      return this.createSaida(transacao.idTransacao!, matUsuario);
    } catch (error: any) {
      console.error('Error in createSaidaTransaction:', error.response?.data || error.message);
      throw error;
    }
  }

  async getNotaFiscalByCodNf(codNf: string): Promise<Transacao | null> {
    try {
      const { data } = await api.get(`/api/v1/transacoes/?codNf=${codNf}`);
      if (data.results && data.results.length > 0) {
        return data.results[0]; 
      }
      return null;
    } catch {
      return null;
    }
  }

  async getNotaFiscalByCodNfAndFornecedor(codNf: string, codFornecedor: number): Promise<Transacao | null> {
    try {
      const { data } = await api.get(`/api/v1/transacoes/?codNf=${codNf}&codFornecedor=${codFornecedor}`);
      if (data.results && data.results.length > 0) {
        return data.results[0];
      }
      return null;
    } catch {
      return null;
    }
  }

  // Método para buscar transações combinadas (usando o novo endpoint otimizado)
  async getUnifiedTransactions(params?: TransactionSearchParams): Promise<Paginated<FormattedTransaction>> {
    console.log('getUnifiedTransactions: Starting with params:', params);
    
    // Check cache first
    const cacheKey = transactionCache.generateKey('unified-transactions', params);
    const cachedData = transactionCache.get<Paginated<FormattedTransaction>>(cacheKey);
    
    if (cachedData) {
      console.log('getUnifiedTransactions: Returning data from cache');
      return cachedData;
    }
    
    // Build URL with parameters
    let url = '/api/v1/unified-transactions/';
    const queryParams: string[] = [];
    
    if (params?.page) {
      queryParams.push(`page=${params.page}`);
    }
    if (params?.dateFrom) {
      // Convert and validate DD/MM/YYYY to ISO format YYYY-MM-DD
      const convertedDateFrom = safeFormatBrazilianDateToISO(params.dateFrom);
      if (convertedDateFrom) {
        queryParams.push(`dateFrom=${encodeURIComponent(convertedDateFrom)}`);
      } else {
        console.warn('Invalid dateFrom format:', params.dateFrom);
      }
    }
    if (params?.dateTo) {
      // Convert and validate DD/MM/YYYY to ISO format YYYY-MM-DD
      const convertedDateTo = safeFormatBrazilianDateToISO(params.dateTo);
      if (convertedDateTo) {
        queryParams.push(`dateTo=${encodeURIComponent(convertedDateTo)}`);
      } else {
        console.warn('Invalid dateTo format:', params.dateTo);
      }
    }
    if (params?.notaFiscal) {
      queryParams.push(`notaFiscal=${encodeURIComponent(params.notaFiscal)}`);
    }
    if (params?.sku) {
      queryParams.push(`sku=${encodeURIComponent(params.sku)}`);
    }
    if (params?.description) {
      queryParams.push(`description=${encodeURIComponent(params.description)}`);
    }
    if (params?.showInUSD !== undefined) {
      queryParams.push(`showInUSD=${params.showInUSD}`);
    }
    if (params?.ordering) {
      queryParams.push(`ordering=${encodeURIComponent(params.ordering)}`);
    }
    if (params?.page_size) {
      queryParams.push(`page_size=${params.page_size}`);
    }
    
    if (queryParams.length > 0) {
      url += `?${queryParams.join('&')}`;
    }
    
    console.log('getUnifiedTransactions: Making API call with URL:', url);
    
    try {
      const { data } = await api.get(url);
      console.log('getUnifiedTransactions: Response received', data.results.length, 'transactions');
      
      // Store data in cache
      transactionCache.set(cacheKey, data);
      
      // Return paginated response
      return data;
    } catch (error) {
      console.error('Error in getUnifiedTransactions:', error);
      return { results: [], count: 0, next: null, previous: null };
    }
  }

  // Método para buscar transações (agora usa apenas o endpoint unificado)
  async getTransactions(params?: TransactionSearchParams): Promise<Paginated<FormattedTransaction>> {
    return await this.getUnifiedTransactions(params);
  }

  async updateTransacao(transacao: Transacao): Promise<Transacao> {
    const { data } = await api.put(`/api/v1/transacoes/${transacao.idTransacao}/`, transacao);
    return data;
  }

  // Métodos CRUD 
  async updateEntrada(entrada: Entrada): Promise<Entrada> {
    const { data } = await api.put(`/api/v1/entradas/${entrada.codEntrada}/`, entrada);
    return data;
  }

  async updateSaida(saida: Saida): Promise<Saida> {
    const { data } = await api.put(`/api/v1/saidas/${saida.codPedido}/`, saida);
    return data;
  }

  // Métodos para deletar
  async deleteEntrada(codEntrada: number): Promise<void> {
    await api.delete(`/api/v1/entradas/${codEntrada}/`);
  }

  async deleteSaida(codPedido: number): Promise<void> {
    await api.delete(`/api/v1/saidas/${codPedido}/`);
  }

  async deleteTransacao(idTransacao: number): Promise<void> {
    await api.delete(`/api/v1/transacoes/${idTransacao}/`);
  }

  // Método para recalcular custos (agora delegado para o backend)
  async recalculateSubsequentSaidaCosts(transactionId: number, sku: string): Promise<void> {
    try {
      const { data } = await api.post('/api/v1/recalculate-costs/', {
        transactionId,
        sku
      });
      
      if (!data.success) {
        throw new Error(data.message || 'Erro ao recalcular custos');
      }
      
      // Clear cache after recalculating costs
      transactionCache.clearEndpoint('unified-transactions');
    } catch (error: any) {
      console.error('Error recalculating costs:', error.response?.data || error.message);
      throw error;
    }
  }

  // Verifica se uma operação manterá o estoque positivo (agora delegado para o backend)
  async validateStockWouldRemainPositive(
    sku: string, 
    operationType: 'delete' | 'edit',
    transactionId?: number, 
    newQuantity?: number
  ): Promise<boolean> {
    try {
      const { data } = await api.post('/api/v1/validate-stock-operation/', {
        sku,
        operationType,
        transactionId,
        newQuantity
      });
      
      return data.valid;
    } catch (error: any) {
      console.error('Error validating stock operation:', error.response?.data || error.message);
      return false;
    }
  }

  // Método genérico para deletar uma transação pelo ID
  async deleteTransaction(transactionId: string): Promise<void> {
    try {
      // Usar o novo endpoint do backend que faz toda a validação e recálculo
      const { data } = await api.delete(`/api/v1/transactions/${transactionId}/`);
      
      if (!data.success) {
        throw new Error(data.message || 'Erro ao excluir transação');
      }
      
      // Clear cache after deleting a transaction
      transactionCache.clearEndpoint('unified-transactions');
    } catch (error: any) {
      console.error('Error deleting transaction:', error.response?.data || error.message);
      throw error;
    }
  }

  // Método para atualizar uma transação (entrada ou saída)
  async updateTransaction(transaction: FormattedTransaction): Promise<void> {
    try {
      // Preparar dados para envio
      const updateData: any = {
        quantity: transaction.quantity,
        unitCost: transaction.unitCost
      };

      // Adicionar campos específicos para entradas
      if (transaction.transactionType === 'entrada') {
        if (transaction.notaFiscal) {
          updateData.codNf = transaction.notaFiscal;
        }
        // Note: supplierId não está disponível na interface FormattedTransaction
        // Se necessário, adicionar à interface ou obter de outra forma
      }

      // Usar o novo endpoint do backend que faz toda a validação e recálculo
      const { data } = await api.put(`/api/v1/transactions/${transaction.id}/update/`, updateData);
      
      if (!data.success) {
        throw new Error(data.message || 'Erro ao atualizar transação');
      }
      
      // Clear cache after updating a transaction
      transactionCache.clearEndpoint('unified-transactions');
    } catch (error: any) {
      console.error('Error updating transaction:', error.response?.data || error.message);
      throw error;
    }
  }
}

export const transactionService = new TransactionService()
