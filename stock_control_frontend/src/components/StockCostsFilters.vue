<!-- StockCostsFilters.vue -->
<template>
    <BaseFilterForm :fields="fields" v-model="filters" @search="onSearch" />
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import type { FilterField } from '@/types/filter';
import BaseFilterForm from './BaseFilterForm.vue';
import { getCurrentBrazilianDate, formatBrazilianDateToISO } from '@/utils/date';

interface StockFilters {
    stockDate: string;
    itemSKU: string;
    itemDescription: string;
    showOnlyStockItems: boolean;
    showOnlyActiveItems: boolean;
    showInUSD: boolean;
}

const filters = ref<StockFilters>({
    stockDate: getCurrentBrazilianDate(),
    itemSKU: '',
    itemDescription: '',
    showOnlyStockItems: true,
    showOnlyActiveItems: true,
    showInUSD: false,
});

// Inicializa a data atual no carregamento do componente
onMounted(() => {
    filters.value.stockDate = getCurrentBrazilianDate();
});

// define os campos para esse formulário
const fields: FilterField<StockFilters>[] = [
    { key: 'stockDate', label: 'Estoque do dia:', type: 'date' },
    { key: 'itemSKU', label: 'SKU do produto:', type: 'text' },
    { key: 'itemDescription', label: 'Descrição do produto:', type: 'text' },
    { key: 'showOnlyStockItems', label: 'Exibir apenas itens com estoque', type: 'checkbox' },
    { key: 'showOnlyActiveItems', label: 'Exibir apenas itens ativos', type: 'checkbox' },
    { key: 'showInUSD', label: 'Exibir valores em USD', type: 'checkbox' },
];

const emit = defineEmits<{
    (e: 'update:modelValue', value: StockFilters): void;
    (e: 'search'): void;
}>();

// dispara busca
function onSearch() {
    console.log('Buscar com filtros:', filters.value);
    
    // Converte a data brasileira para ISO antes de enviar
    const convertedFilters = { ...filters.value };
    if (convertedFilters.stockDate && convertedFilters.stockDate.includes('/')) {
        convertedFilters.stockDate = formatBrazilianDateToISO(convertedFilters.stockDate);
    }
    
    emit('update:modelValue', convertedFilters);
    emit('search');
}

// observa mudanças nos filtros e notifica o pai
watch(filters, (newValue) => {
    emit('update:modelValue', { ...newValue });
}, { deep: true });
</script>