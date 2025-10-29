import api from './api'
import { type Paginated } from '@/types/api'
import { createLogger } from '@/utils/logger'

const logger = createLogger('StockService')

export interface StockItemDTO {
  cod_sku: string | number
  descricao_item: string
  unid_medida: string
  active: boolean
  quantity: number
  estimated_consumption_time: string | null
}

/** Modelagem frontend em camelCase */
export interface StockItem {
  codSku: string | number
  descricaoItem: string
  unidMedida: string
  active: boolean
  quantity: number
  estimatedConsumptionTime: string | null
}

class StockService {
  /** Lista itens de estoque paginados, com suporte a filtros e ordenação */
  async getStockItems(page = 1, filters: Partial<{ 
    codSku: string | number; 
    descricaoItem: string; 
    stockDate: string;
    showOnlyStockItems: boolean;
    showOnlyActiveItems: boolean;
    page_size?: number;
    ordering?: string;
  }> = {}): Promise<Paginated<StockItem>> {
    try {
      logger.debug('Iniciando busca de itens em estoque')
      logger.debug('Filtros recebidos:', filters)
      
      const params = new URLSearchParams({ page: String(page) })
      
      // Usar camelCase diretamente nos parâmetros
      if (filters.codSku) params.append('codSku', String(filters.codSku))
      if (filters.descricaoItem) params.append('descricaoItem', filters.descricaoItem)
      // convert DD/MM/YYYY to YYYY-MM-DD format
      let d = filters.stockDate || ''
        if (filters.stockDate && filters.stockDate.includes('/')) {
            const parts = filters.stockDate.split('/')
            if (parts.length === 3) {
            d = `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`
            }
        }
      if (filters.stockDate) params.append('stockDate', String(d))
      if (filters.showOnlyStockItems !== undefined) params.append('showOnlyStockItems', String(filters.showOnlyStockItems))
      if (filters.showOnlyActiveItems !== undefined) params.append('showOnlyActiveItems', String(filters.showOnlyActiveItems))
      
      // Adicionar parâmetros de paginação e ordenação
      if (filters.page_size) params.append('page_size', String(filters.page_size))
      if (filters.ordering) params.append('ordering', filters.ordering)
      
      logger.debug('Params construídos:', params.toString())
      
      const url = `/api/v1/stocks/?${params.toString()}`
      logger.debug('URL da requisição:', url)
      
      const response = await api.get(url)
      logger.debug('Resposta da API:', response.data)
      
      return response.data
    } catch (error) {
      logger.error('Erro ao buscar itens em estoque:', error)
      throw error
    }
  }
}

export const stockService = new StockService() 