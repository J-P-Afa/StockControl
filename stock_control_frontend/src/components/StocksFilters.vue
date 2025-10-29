<template>
    <BaseFilterForm
      :fields="fields"
      v-model="filters"
      @search="onSearch"
    />
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, watch } from 'vue';
  import type { FilterField } from '@/types/filter';
  import BaseFilterForm from './BaseFilterForm.vue';
  import { getCurrentBrazilianDate, formatBrazilianDateToISO } from '@/utils/date';
  
  interface StockFilters {
    stockDate: string;
    itemSKU: string;
    itemDescription: string;
    showOnlyStockItems: boolean;
    showOnlyActiveItems: boolean;
  }
  
  const filters = ref<StockFilters>({
    stockDate: getCurrentBrazilianDate(),
    itemSKU: '',
    itemDescription: '',
    showOnlyStockItems: true,
    showOnlyActiveItems: true,
  });
  
  // Emitir evento para atualizar o componente pai
  const emit = defineEmits(['update:filters']);
  
  // inicializa a data com o dia atual
  onMounted(() => {
    filters.value.stockDate = getCurrentBrazilianDate();
    
    // Emite o evento com os filtros iniciais
    emit('update:filters', { ...filters.value });
  });
  
  // Observa mudanças nos filtros para emitir eventos
  watch(filters, (newFilters) => {
    emit('update:filters', { ...newFilters });
  }, { deep: true });
  
  // define os campos para esse formulário
  const fields: FilterField<StockFilters>[] = [
    { key: 'stockDate',             label: 'Estoque do dia:',                     type: 'date' },
    { key: 'itemSKU',               label: 'SKU do produto:',                     type: 'text'},
    { key: 'itemDescription',       label: 'Descrição do produto:',               type: 'text'},
    { key: 'showOnlyStockItems',    label: 'Apenas itens com estoque:',     type: 'checkbox'},
    { key: 'showOnlyActiveItems',   label: 'Apenas itens ativos:',          type: 'checkbox'},
  ];
  
  // dispara busca
  function onSearch(vals: Record<string, any>) {
    const filters = vals as StockFilters;
    console.log('Buscar com filtros:', vals);
    
    // Converte a data brasileira para ISO antes de enviar
    const convertedVals = { ...vals };
    if (convertedVals.stockDate && convertedVals.stockDate.includes('/')) {
      convertedVals.stockDate = formatBrazilianDateToISO(convertedVals.stockDate);
    }
    
    emit('update:filters', convertedVals);
  }
  </script>
  