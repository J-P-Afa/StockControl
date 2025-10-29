<template>
  <PageContainer
    title="Consulta de Estoque"
    :global-loading="loading"
    :error="error"
    @retry="loadStocks"
  >
    <div class="stocks-content">
      <!-- Filtros -->
      <div class="filters-section">
        <h3>Filtros de Busca</h3>
        <StocksFilters @update:filters="updateFilters" />
      </div>

      <!-- Lista de Produtos -->
      <div class="stocks-section">
        <h3>Lista de Produtos em Estoque</h3>
        <StockItemsList :filters="stockFilters" />
      </div>
    </div>
  </PageContainer>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import StocksFilters from '@/components/StocksFilters.vue';
import StockItemsList from '@/components/StockItemsList.vue';
import PageContainer from '@/components/PageContainer.vue';
import { usePageState } from '@/composables/usePageState';
import { useErrorHandler } from '@/composables/useApiError';

// Composables
const { handleError } = useErrorHandler();
const { loading, error, execute } = usePageState();

// Define o estado dos filtros compartilhados
const stockFilters = ref({
  stockDate: '',
  itemSKU: '',
  itemDescription: '',
  showOnlyStockItems: true,
  showOnlyActiveItems: true,
});

// Métodos
const loadStocks = async () => {
  await execute(async () => {
    // Simula carregamento de dados da página
    await new Promise(resolve => setTimeout(resolve, 500));
    return { message: 'Estoque carregado' };
  });
};

// Atualiza os filtros quando o componente filho emite o evento
function updateFilters(newFilters: typeof stockFilters.value) {
  stockFilters.value = { ...newFilters };
}
</script>

<style scoped>
.stocks-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.filters-section,
.stocks-section {
  /*background: var(--color-dark-bg);*/
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.filters-section h3,
.stocks-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  /*color: #1f2937;*/
}

@media (max-width: 768px) {
  .stocks-content {
    gap: 16px;
  }
  
  .filters-section,
  .stocks-section {
    padding: 16px;
  }
}
</style>
