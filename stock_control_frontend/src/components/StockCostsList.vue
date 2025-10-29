<template>
    <div>
      <BaseTable
        v-if="!loading"
        :columns="columns"
        :rows="items"
        :sortKey="pagination.sortKey.value"
        :sortOrder="pagination.sortOrder.value"
        keyField="sku"
        @update:sort="handleSort"
      >
        <!-- Formatação para quantidade zero -->
        <template #cell-quantity="{ value }">
          <span :class="{ 'text-muted': value === 0 }">
            {{ value }}
          </span>
        </template>
        
        <!-- Formatação para valor unitário -->
        <template #cell-unitCost="{ value, row }">
          {{ formatCurrency(value, row.currency || 'BRL') }}
        </template>
        
        <!-- Formatação para valor total -->
        <template #cell-totalCost="{ value, row }">
          {{ formatCurrency(value, row.currency || 'BRL') }}
        </template>
      </BaseTable>
      <div v-else class="loading">Carregando custos de estoque...</div>
      
      <PaginationControls
        :current-page="pagination.currentPage.value"
        :total-pages="pagination.totalPages.value"
        :total-items="pagination.totalItems.value"
        :page-size="pagination.pageSize.value"
        @go-to-page="pagination.goToPage"
        @change-page-size="pagination.updatePageSize"
      />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, computed, watch, onMounted } from 'vue';
  import BaseTable from '@/components/BaseTable.vue';
  import PaginationControls from '@/components/PaginationControls.vue';
  import { usePagination } from '@/composables/usePagination';
  import type { ColumnDef } from '@/composables/useTable';
  import { stockCostService, type StockCost } from '@/services/stockCostService';
  import formatCurrency from '@/utils/currency';
  const props = defineProps<{
    filters: {
      stockDate: string;
      itemSKU: string;
      itemDescription: string;
      showOnlyStockItems: boolean;
      showOnlyActiveItems: boolean;
      showInUSD: boolean;
    }
    refreshKey?: number
  }>();
  
  const loading = ref(false);
  const items = ref<StockCost[]>([]);
  
  // Configurar paginação
  const pagination = usePagination({
    pageSize: 10,
    initialPage: 1,
    initialSort: { key: 'sku', order: 'asc' }
  });
  
  // definindo colunas
  const columns: ColumnDef<StockCost>[] = [
    { key: 'sku', label: 'SKU', sortable: true },
    { key: 'description', label: 'Descrição do Produto', sortable: true },
    { key: 'quantity', label: 'Quantidade em Estoque', sortable: true },
    { key: 'unityMeasure', label: 'Unidade de Medida', sortable: true },
    { key: 'unitCost', label: 'Custo Unitário', sortable: true },
    { key: 'totalCost', label: 'Custo Total', sortable: true },
  ];
  
  // busca os custos de estoque da API
  async function fetchStockCosts() {
    try {
      loading.value = true;
      
      // Mapeia os filtros para o formato esperado pelo serviço
      const serviceFilters: Record<string, any> = {};
      
      if (props.filters.itemSKU) {
        serviceFilters.sku = props.filters.itemSKU;
      }
      
      if (props.filters.itemDescription) {
        serviceFilters.description = props.filters.itemDescription;
      }
      
      if (props.filters.showOnlyStockItems) {
        serviceFilters.hasStock = true;
      }
      
      if (props.filters.showOnlyActiveItems) {
        serviceFilters.active = true;
      }
      
      if (props.filters.showInUSD) {
        serviceFilters.showInUSD = true;
      }
      
      // Adicionar parâmetros de paginação e ordenação
      const queryParams = pagination.getQueryParams();
      serviceFilters.ordering = queryParams.ordering;
      serviceFilters.page_size = queryParams.page_size;
      
      const result = await stockCostService.getStockCosts(
        parseInt(queryParams.page),
        {
          ...serviceFilters,
          stockDate: props.filters.stockDate
        }
      );
      
      items.value = result.results;
      pagination.updateTotalItems(result.count);
    } catch (error) {
      console.error('Erro ao buscar custos de estoque:', error);
    } finally {
      loading.value = false;
    }
  }
  
  // Função para ordenar
  function handleSort(key: string) {
    pagination.setSort(key);
  }
  
  // busca inicial
  onMounted(() => {
    fetchStockCosts();
  });
  
  // reagir a mudanças de filtros ou refreshKey
  watch(
    [() => props.filters, () => props.refreshKey],
    () => {
      pagination.reset();
      fetchStockCosts();
    },
    { deep: true }
  );
  
  // reagir a mudanças de paginação e ordenação
  watch([
    () => pagination.currentPage.value,
    () => pagination.sortKey.value,
    () => pagination.sortOrder.value,
    () => pagination.pageSize.value
  ], () => {
    fetchStockCosts();
  });
  </script>
  