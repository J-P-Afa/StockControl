<!-- TransactionsFilters.vue -->
<template>
    <BaseFilterForm :fields="fields" v-model="filters" @search="onSearch" />
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import type { FilterField } from '@/types/filter'
import BaseFilterForm from './BaseFilterForm.vue'
import type { TransactionSearchParams } from '@/services/transactionService'
import { getCurrentBrazilianDate, safeFormatBrazilianDateToISO } from '@/utils/date'

// Interface for the filter form
interface TransactionFilters {
    transactionsDateFrom: string;
    transactionsDateTo: string;
    itemSKU: string;
    itemDescription: string;
    notaFiscal: string;
    showInUSD: boolean;
}

// Define emits for communication with parent component
const emit = defineEmits<{
    (e: 'update:modelValue', value: TransactionFilters): void;
    (e: 'search'): void;
}>();

// Get today's date in Brazilian format for default values
const today = getCurrentBrazilianDate();

// Local filter state
const filters = ref<TransactionFilters>({
    transactionsDateFrom: today,
    transactionsDateTo: today,
    itemSKU: '',
    itemDescription: '',
    notaFiscal: '',
    showInUSD: false
});

// Form fields
const fields: FilterField<TransactionFilters>[] = [
    { key: 'transactionsDateFrom', label: 'Data inicial:', type: 'date' },
    { key: 'transactionsDateTo', label: 'Data final:', type: 'date' },
    { key: 'notaFiscal', label: 'Número NF:', type: 'text' },
    { key: 'itemSKU', label: 'SKU do produto:', type: 'text' },
    { key: 'itemDescription', label: 'Descrição do produto:', type: 'text' },
    { key: 'showInUSD', label: 'Exibir valores em USD', type: 'checkbox' }
];

// When the user clicks search
function onSearch() {
    console.log('TransactionsFilters: Search button clicked');
    console.log('TransactionsFilters: Current filters:', filters.value);
    
    try {
        // Convert and validate Brazilian dates to ISO format before sending
        const convertedFilters = { ...filters.value };
        
        if (convertedFilters.transactionsDateFrom) {
            const convertedFrom = safeFormatBrazilianDateToISO(convertedFilters.transactionsDateFrom);
            if (convertedFrom) {
                convertedFilters.transactionsDateFrom = convertedFrom;
            } else {
                console.warn('Invalid dateFrom format:', convertedFilters.transactionsDateFrom);
                return; // Don't proceed with invalid date
            }
        }
        
        if (convertedFilters.transactionsDateTo) {
            const convertedTo = safeFormatBrazilianDateToISO(convertedFilters.transactionsDateTo);
            if (convertedTo) {
                convertedFilters.transactionsDateTo = convertedTo;
            } else {
                console.warn('Invalid dateTo format:', convertedFilters.transactionsDateTo);
                return; // Don't proceed with invalid date
            }
        }
        
        // First update the model
        emit('update:modelValue', convertedFilters);
        console.log('TransactionsFilters: Emitted update:modelValue event');
        
        // Then trigger search event
        emit('search');
        console.log('TransactionsFilters: Emitted search event');
    } catch (error) {
        console.error('TransactionsFilters: Error emitting events:', error);
    }
}

// Log component initialization
onMounted(() => {
    console.log('TransactionsFilters: Component mounted');
    console.log('TransactionsFilters: Initial filters:', filters.value);
});

// Watch for filter changes and notify parent
watch(filters, (newValue) => {
    console.log('TransactionsFilters: Filters updated:', newValue);
    emit('update:modelValue', { ...newValue });
}, { deep: true });
</script>
