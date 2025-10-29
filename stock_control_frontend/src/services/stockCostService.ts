import api from '@/services/api'
import type { Paginated } from '@/types/api'

export interface StockCost {
  sku: string
  description: string
  quantity: number
  unityMeasure: string
  unitCost: number
  totalCost: number
  active: boolean
  lastEntryCost: number
  currency?: string
}

export const stockCostService = {
  async getStockCosts(
    page = 1, 
    filters?: { 
      stockDate?: string; 
      sku?: string; 
      description?: string; 
      hasStock?: boolean; 
      active?: boolean; 
      showInUSD?: boolean;
      ordering?: string;
      page_size?: number;
    }
  ): Promise<Paginated<StockCost>> {
    try {
      const params = new URLSearchParams({ page: String(page) });
      
      if (filters?.stockDate) {
        params.append('stockDate', filters.stockDate);
      }
      if (filters?.sku) {
        params.append('sku', filters.sku);
      }
      if (filters?.description) {
        params.append('description', filters.description);
      }
      if (filters?.hasStock !== undefined) {
        params.append('hasStock', String(filters.hasStock));
      }
      if (filters?.active !== undefined) {
        params.append('active', String(filters.active));
      }
      if (filters?.showInUSD !== undefined) {
        params.append('showInUSD', String(filters.showInUSD));
      }
      if (filters?.ordering) {
        params.append('ordering', filters.ordering);
      }
      if (filters?.page_size) {
        params.append('page_size', String(filters.page_size));
      }
      
      const url = `/api/v1/stock-costs/?${params.toString()}`;
      const response = await api.get(url);
      
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar custos de estoque:', error)
      throw error
    }
  },
} 