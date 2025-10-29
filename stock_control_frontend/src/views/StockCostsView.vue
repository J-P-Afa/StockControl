<template>
  <PageContainer
    title="Custos do Estoque"
    :global-loading="loading"
    :error="error || undefined"
    @retry="loadStockCosts"
  >
    <div class="stock-costs-content">
      <!-- Filtros -->
      <div class="filters-section">
        <h3>Filtros de Busca</h3>
        <StockCostsFilters v-model="filters" @search="onSearch" />
      </div>

      <!-- Lista de Custos -->
      <div class="costs-section">
        <h3>Lista de Custos por Produto</h3>
        <StockCostsList :filters="filters" :refreshKey="refreshKey" />
      </div>
    </div>
  </PageContainer>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import StockCostsFilters from '@/components/StockCostsFilters.vue';
import StockCostsList from '@/components/StockCostsList.vue';
import PageContainer from '@/components/PageContainer.vue';
import { usePageState } from '@/composables/usePageState';
import { useErrorHandler } from '@/composables/useApiError';

// Composables
const { handleError } = useErrorHandler();
const { loading, error, execute } = usePageState();

interface StockFilters {
  stockDate: string;
  itemSKU: string;
  itemDescription: string;
  showOnlyStockItems: boolean;
  showOnlyActiveItems: boolean;
  showInUSD: boolean;
}

const filters = ref<StockFilters>({
  stockDate: '',
  itemSKU: '',
  itemDescription: '',
  showOnlyStockItems: false,
  showOnlyActiveItems: true,
  showInUSD: false,
});

// chave reativa para forçar reload da lista
const refreshKey = ref(0);

// Métodos
const loadStockCosts = async () => {
  await execute(async () => {
    // Simula carregamento de dados da página
    await new Promise(resolve => setTimeout(resolve, 500));
    return { message: 'Custos do estoque carregados' };
  });
};

// função para atualizar a lista quando os filtros forem aplicados
function onSearch() {
  console.log('StockCostsView: Aplicando filtros:', filters.value);
  refreshKey.value++;
}
</script>

<style scoped>
.stock-costs-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filters-section,
.costs-section {
  /* background: white; */
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.filters-section h3,
.costs-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  /*color: #1f2937;*/
}

@media (max-width: 768px) {
  .stock-costs-content {
    gap: 16px;
  }
  
  .filters-section,
  .costs-section {
    padding: 16px;
  }
}
</style>
