<!-- TransactionsList.vue -->
<template>
    <div class="transactions-table">
        <div v-if="loading" class="loading-container">
            <p>Carregando transações...</p>
        </div>
        <div v-else-if="error" class="error-container">
            <p>Erro ao carregar transações: {{ error }}</p>
        </div>
        <div v-else-if="transactions.length === 0" class="empty-state">
            <p>Nenhuma transação encontrada.</p>
            <div class="empty-state-suggestions">
                <p><strong>Sugestões:</strong></p>
                <ul>
                    <li>Verifique se as datas estão corretas</li>
                    <li>Tente ampliar o intervalo de datas</li>
                    <li>Remova alguns filtros para ver mais resultados</li>
                    <li>Verifique se há transações cadastradas no sistema</li>
                </ul>
            </div>
        </div>
        <BaseTable 
            v-else
            :columns="columns" 
            :rows="transactions" 
            :sortKey="pagination.sortKey.value"
            :sortOrder="pagination.sortOrder.value" 
            keyField="id"
            @update:sort="handleSort" 
        >
            <template #cell-transactionType="{ value }">
                <span :class="['badge', value === 'Entrada' ? 'entrada' : 'saida']">
                    {{ value }}
                </span>
            </template>

            <template #cell-cronology="{ value }">
                {{ formatInteger(value) }}
            </template>

            <template #cell-notaFiscal="{ value }">
                {{ formatInteger(value) }}
            </template>

            <template #cell-quantity="{ value }">
                {{ formatDecimal(value) }}
            </template>

            <template #cell-cost="{ value, row }">
                {{ formatCurrency(value, row.currency || 'BRL') }}
            </template>

            <!--<template #cell-edit="{ row }">
                <button class="btn-edit table-btn" @click="onEdit(row)">
                    Editar
                </button>
            </template>-->
            <template #cell-delete="{ row }">
                <button class="btn-delete table-btn" @click="onDelete(row)">
                    Deletar
                </button>
            </template>
        </BaseTable>
        
        <PaginationControls
            v-if="!loading && !error && transactions.length > 0"
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
import { ref, onMounted, watch, computed } from 'vue';
import BaseTable from './BaseTable.vue';
import PaginationControls from '@/components/PaginationControls.vue';
import { usePagination } from '@/composables/usePagination';
import type { ColumnDef } from '@/composables/useTable';
import { parseBrazilianDate, formatDateToBrazilian } from '@/utils/date';
import { transactionService, type FormattedTransaction, type TransactionSearchParams } from '@/services/transactionService';
import formatCurrency from '@/utils/currency';
import { formatInteger, formatDecimal, parseInteger, parseDecimal } from '@/utils/numbersFormat';

// Extended column definition with formatter and html
interface ExtendedColumnDef<T> extends ColumnDef<T> {
  formatter?: (value: any, row?: any) => string;
  html?: boolean;
}

// Interface for table
interface Transaction {
    id: string;
    cronology: number;
    date: string;
    time: string;
    sku: string;
    description: string;
    quantity: number;
    unityMeasure: string;
    cost: number;
    unitCost: number;
    transactionType: string;
    notaFiscal?: string; // Optional - only for entries
    username: string;
    currency?: string;
    // edit: string; // Placeholder for edit button column
    delete: string; // Placeholder for delete button column
}

// Interface for raw filters from parent component
interface TransactionFilters {
  transactionsDateFrom: string;
  transactionsDateTo: string;
  itemSKU: string;
  itemDescription: string;
  notaFiscal: string;
  showInUSD: boolean;
}

// Props to receive filters from parent component
const props = defineProps<{
    filters?: TransactionFilters
    refreshKey?: number
}>();

// Convert from parent filters to service params format
const serviceParams = computed<TransactionSearchParams>(() => {
    if (!props.filters) return {};
    
    const params = {
        dateFrom: props.filters.transactionsDateFrom || undefined,
        dateTo: props.filters.transactionsDateTo || undefined,
        sku: props.filters.itemSKU === '' ? undefined : props.filters.itemSKU,
        description: props.filters.itemDescription === '' ? undefined : props.filters.itemDescription,
        notaFiscal: props.filters.notaFiscal === '' ? undefined : props.filters.notaFiscal,
        showInUSD: props.filters.showInUSD
    };
    
    console.log('TransactionsList: Computed serviceParams:', params);
    return params;
});

// Emit events to parent
const emit = defineEmits<{
    (e: 'edit', transaction: Transaction): void
    (e: 'delete', transaction: Transaction): void
}>();

// State
const transactions = ref<Transaction[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

// Configurar paginação
const pagination = usePagination({
  pageSize: 10,
  initialPage: 1,
  initialSort: { key: 'cronology', order: 'desc' }
});

// Load transactions with filters
async function fetchTransactions() {
    console.log('TransactionsList: fetchTransactions called');
    console.log('TransactionsList: Raw filters:', props.filters);
    console.log('TransactionsList: Converted params:', serviceParams.value);
    
    loading.value = true;
    error.value = null;
    
    try {
        console.log('TransactionsList: Calling API with params:', JSON.stringify(serviceParams.value));
        
        // Adicionar parâmetros de paginação e ordenação
        const queryParams = pagination.getQueryParams();
        const apiParams = {
            ...serviceParams.value,
            page: parseInt(queryParams.page),
            ordering: queryParams.ordering,
            page_size: parseInt(queryParams.page_size)
        };
        
        // Use converted params for the API call
        const result = await transactionService.getTransactions(apiParams);
        
        console.log('TransactionsList: API call result:', result);
        
        // Convert from FormattedTransaction to table format
        transactions.value = result.results.map((item, index) => ({
            id: item.id,
            cronology: item.idTransacao,
            date: formatDateToBrazilian(item.date),
            time: item.time,
            sku: item.sku,
            description: item.description,
            quantity: item.quantity,
            unityMeasure: item.unityMeasure,
            unitCost: item.unitCost,
            cost: item.totalCost,
            transactionType: item.transactionType === 'entrada' ? 'Entrada' : 'Saída',
            notaFiscal: item.notaFiscal,
            username: item.username || 'N/A',
            currency: item.currency || 'BRL',
            // edit: '', // Placeholder for edit button
            delete: '', // Placeholder for delete button
        }));
        
        // Atualizar informações de paginação
        pagination.updateTotalItems(result.count);
    } catch (err) {
        console.error('Erro ao carregar transações:', err);
        error.value = 'Não foi possível carregar as transações. Tente novamente mais tarde.';
        transactions.value = [];
    } finally {
        loading.value = false;
    }
}

// Função para ordenar
function handleSort(key: string) {
    pagination.setSort(key);
}

// Load initial data when component is mounted
onMounted(() => {
    console.log('TransactionsList: Component mounted');
    fetchTransactions();
});

// Reload when filters or refreshKey change
watch([() => props.filters, () => props.refreshKey], ([newFilters, newRefreshKey], [oldFilters, oldRefreshKey]) => {
    console.log('TransactionsList: Watch triggered');
    console.log('TransactionsList: New filters:', newFilters);
    console.log('TransactionsList: Old filters:', oldFilters);
    console.log('TransactionsList: New refreshKey:', newRefreshKey);
    console.log('TransactionsList: Old refreshKey:', oldRefreshKey);
    
    // Check if filters have changed
    if (JSON.stringify(newFilters) !== JSON.stringify(oldFilters)) {
        console.log('TransactionsList: Filters have changed, fetching new data');
        pagination.reset();
        fetchTransactions();
    }
    // Check if refreshKey has changed
    else if (newRefreshKey !== oldRefreshKey) {
        console.log('TransactionsList: RefreshKey has changed, fetching new data');
        pagination.reset();
        fetchTransactions();
    }
    else {
        console.log('TransactionsList: No significant changes detected');
    }
}, { deep: true });

// reagir a mudanças de paginação e ordenação
watch([
    () => pagination.currentPage.value,
    () => pagination.sortKey.value,
    () => pagination.sortOrder.value,
    () => pagination.pageSize.value
], () => {
    fetchTransactions();
});

// Table columns
const columns: ExtendedColumnDef<Transaction>[] = [
    { 
        key: 'cronology', 
        label: 'Cronologia', 
        sortable: true,
        sortFn: (a, b, order) => {
            const timeA = parseInteger(a.cronology.toString()) || 0;
            const timeB = parseInteger(b.cronology.toString()) || 0;
            return order === 'asc' ? timeA - timeB : timeB - timeA;
        }
    },
    { 
        key: 'transactionType', 
        label: 'Tipo', 
        sortable: true,
        html: true
    },
    {
        key: 'date',
        label: 'Data',
        sortable: true,
        sortFn: (a, b, order) => {
            const timeA = parseBrazilianDate(a.date) || 0;
            const timeB = parseBrazilianDate(b.date) || 0;
            return order === 'asc' ? timeA - timeB : timeB - timeA;
        }
    },
    {
        key: 'time',
        label: 'Hora',
        sortable: true
    },
    { 
        key: 'notaFiscal', 
        label: 'Número NF',
        sortable: true,
        sortFn: (a, b, order) => {
            const timeA = parseInteger(a.notaFiscal || '0') || 0;
            const timeB = parseInteger(b.notaFiscal || '0') || 0;
            return order === 'asc' ? timeA - timeB : timeB - timeA;
        }
    },
    { key: 'sku', label: 'SKU', sortable: true },
    { key: 'description', label: 'Descrição', sortable: true },
    { 
        key: 'quantity', 
        label: 'Quantidade', 
        sortable: true,
        sortFn: (a, b, order) => {
            const timeA = a.quantity;
            const timeB = b.quantity;
            return order === 'asc' ? timeA - timeB : timeB - timeA;
        }
    },
    { 
        key: 'cost', 
        label: 'Custo da transação', 
        sortable: true,
        sortFn: (a, b, order) => {
            const timeA = parseFloat(a.cost.toString());
            const timeB = parseFloat(b.cost.toString());
            return order === 'asc' ? timeA - timeB : timeB - timeA;
        }
    },
    { key: 'username', label: 'Usuário', sortable: true },
    // { key: 'edit', label: 'Editar', sortable: false },
    { key: 'delete', label: 'Deletar', sortable: false }
];

// Remover o useTable já que agora usamos paginação do backend

// Functions for edit and delete buttons
function onEdit(transaction: Transaction) {
    console.log('TransactionsList: Requesting edit for transaction:', transaction);
    
    // Log field names and values para diagnóstico
    console.log('Available fields:', Object.keys(transaction));
    console.log('unitCost:', transaction.unitCost);
    console.log('cost:', transaction.cost);
    console.log('quantity:', transaction.quantity);
    
    // Converter formato de transactionType para ser compatível com o TransactionForm
    const formattedTransaction = {
        ...transaction,
        transactionType: transaction.transactionType === 'Entrada' ? 'entrada' : 'saida',
        // Garantir que unitCost seja corretamente definido
        unitCost: transaction.unitCost || (transaction.cost !== undefined && transaction.quantity ? transaction.cost / transaction.quantity : 0)
    };
    
    console.log('Formatted transaction for edit:', formattedTransaction);
    emit('edit', formattedTransaction);
}

function onDelete(transaction: Transaction) {
    emit('delete', transaction);
}
</script>

<style scoped>
.empty-state {
    text-align: center;
    padding: 2rem;
    color: #6b7280;
}

.empty-state-suggestions {
    margin-top: 1rem;
    text-align: left;
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
}

.empty-state-suggestions ul {
    list-style-type: disc;
    padding-left: 1.5rem;
    margin-top: 0.5rem;
}

.empty-state-suggestions li {
    margin-bottom: 0.25rem;
    color: #4b5563;
}
</style>
