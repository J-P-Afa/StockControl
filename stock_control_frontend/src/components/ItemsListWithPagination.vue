<template>
  <div class="items-list">
    <BaseTable
      v-if="!loading && items.length > 0"
      :columns="columns"
      :rows="items"
      :sortKey="sortKey"
      :sortOrder="sortOrder"
      keyField="codSku"
      @update:sort="handleSort"
    >
      <template #cell-active="{ value }">
        <span :class="['status-badge', value ? 'status-badge--success' : 'status-badge--danger']">
          {{ value ? 'Ativo' : 'Inativo' }}
        </span>
      </template>
      <template #cell-edit="{ row }">
        <LoadingButton
          variant="secondary"
          size="small"
          @click="onEdit(row)"
        >
          Editar
        </LoadingButton>
      </template>
      <template #cell-delete="{ row }">
        <LoadingButton
          variant="danger"
          size="small"
          @click="onDelete(row)"
        >
          Excluir
        </LoadingButton>
      </template>
    </BaseTable>
    
    <div v-if="loading" class="loading-container">
      <LoadingSpinner size="medium" message="Carregando itens..." />
    </div>
    
    <div v-if="error" class="error-container">
      <div class="error-card">
        <div class="error-icon">⚠️</div>
        <h3>Erro ao carregar itens</h3>
        <p>{{ error }}</p>
        <LoadingButton variant="primary" @click="fetchItems">
          Tentar novamente
        </LoadingButton>
      </div>
    </div>
    
    <div v-if="!loading && !error && items.length === 0" class="empty-container">
      <div class="empty-card">
        <div class="empty-icon">📦</div>
        <h3>Nenhum item encontrado</h3>
        <p>Não há itens que correspondam aos filtros aplicados.</p>
      </div>
    </div>
    
    <PaginationControls
      v-if="!loading && !error && items.length > 0"
      :current-page="currentPage"
      :total-pages="totalPages"
      :total-items="totalItems"
      :page-size="pageSize"
      @go-to-page="goToPage"
      @change-page-size="changePageSize"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import BaseTable from '@/components/BaseTable.vue';
import PaginationControls from '@/components/PaginationControls.vue';
import LoadingButton from '@/components/LoadingButton.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import { usePagination } from '@/composables/usePagination';
import { useErrorHandler } from '@/composables/useApiError';
import type { ColumnDef } from '@/composables/useTable';
import { itemService, type Item } from '@/services/itemService';

// Props para receber filtros do componente pai
const props = defineProps<{
  filters?: {
    codSku?: string;
    descricaoItem?: string;
    unidMedida?: string;
    active?: boolean;
  }
}>();

// Emits para comunicação com componente pai
const emit = defineEmits<{
  edit: [item: Item];
  delete: [item: Item];
}>();

// Composables
const { handleError } = useErrorHandler();

const items = ref<Item[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

// Usar o novo composable de paginação
const pagination = usePagination({
  pageSize: 10,
  initialPage: 1,
  initialSort: { key: 'codSku', order: 'asc' }
});

// Busca itens da API com filtros, paginação e ordenação
async function fetchItems() {
  loading.value = true;
  error.value = null;
  try {
    console.log('ItemsListWithPagination: Buscando itens com filtros:', props.filters);
    console.log('ItemsListWithPagination: Estado da paginação:', pagination.paginationState.value);
    console.log('ItemsListWithPagination: Estado da ordenação:', pagination.sortState.value);
    
    // Preparar parâmetros de query
    const queryParams = {
      ...pagination.getQueryParams(),
      ...props.filters
    };
    
    const result = await itemService.getItems(
      parseInt(queryParams.page), 
      queryParams
    );
    
    items.value = result.results;
    pagination.updateTotalItems(result.count);
  } catch (e) {
    console.error('Erro ao carregar itens:', e);
    error.value = 'Erro ao carregar itens';
    handleError(e, 'Erro ao carregar itens');
  } finally {
    loading.value = false;
  }
}

// Função para mudar de página
function goToPage(page: number) {
  pagination.goToPage(page);
}

// Função para mudar tamanho da página
function changePageSize(size: number) {
  pagination.updatePageSize(size);
}

// Função para ordenar
function handleSort(key: string) {
  pagination.setSort(key);
}

// Funções para editar e deletar
function onEdit(item: Item) {
  emit('edit', item);
}

function onDelete(item: Item) {
  emit('delete', item);
}

// Definir colunas da tabela
const columns: ColumnDef<Item>[] = [
  { key: 'codSku', label: 'SKU', sortable: true },
  { key: 'descricaoItem', label: 'Descrição', sortable: true },
  { key: 'unidMedida', label: 'Unidade', sortable: true },
  { key: 'active', label: 'Ativo', sortable: true },
  { key: 'edit', label: 'Ações', sortable: false },
  { key: 'delete', label: '', sortable: false },
];

// Expor dados para o template
const currentPage = computed(() => pagination.currentPage.value);
const totalPages = computed(() => pagination.totalPages.value);
const totalItems = computed(() => pagination.totalItems.value);
const pageSize = computed(() => pagination.pageSize.value);
const sortKey = computed(() => pagination.sortKey.value);
const sortOrder = computed(() => pagination.sortOrder.value);

// Busca dados quando os filtros mudam
watch(() => props.filters, (newFilters) => {
  console.log('ItemsListWithPagination: Filtros mudaram:', newFilters);
  pagination.reset();
  fetchItems();
}, { deep: true });

// Busca dados quando paginação ou ordenação mudam
watch([
  () => pagination.currentPage.value,
  () => pagination.sortKey.value,
  () => pagination.sortOrder.value,
  () => pagination.pageSize.value
], () => {
  fetchItems();
});

onMounted(() => {
  console.log('ItemsListWithPagination: Component mounted');
  fetchItems();
});
</script>

<style scoped>
.items-list {
  /*background: white;*/
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  padding: 40px 20px;
}

.error-card,
.empty-card {
  text-align: center;
  max-width: 400px;
  padding: 24px;
}

.error-icon,
.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-card h3,
.empty-card h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.error-card p,
.empty-card p {
  margin: 0 0 20px 0;
  color: #6b7280;
  line-height: 1.5;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.status-badge--success {
  background: #dcfce7;
  color: #166534;
}

.status-badge--danger {
  background: #fee2e2;
  color: #991b1b;
}
</style>
