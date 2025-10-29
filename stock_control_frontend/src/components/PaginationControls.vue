<template>
  <div class="pagination-controls" v-if="totalPages > 1">
    <div class="pagination-info">
      <span>
        Página {{ currentPage }} de {{ totalPages }}
        ({{ totalItems }} {{ totalItems === 1 ? 'item' : 'itens' }})
      </span>
    </div>
    
    <div class="pagination-buttons">
      <button 
        :disabled="!hasPreviousPage" 
        @click="$emit('go-to-page', 1)"
        class="pagination-btn"
        title="Primeira página"
      >
        ⏮
      </button>
      
      <button 
        :disabled="!hasPreviousPage" 
        @click="$emit('go-to-page', currentPage - 1)"
        class="pagination-btn"
        title="Página anterior"
      >
        ◀
      </button>
      
      <!-- Páginas numeradas -->
      <template v-for="page in visiblePages" :key="page">
        <button
          v-if="page !== '...'"
          :class="['pagination-btn', 'page-number', { active: page === currentPage }]"
          @click="$emit('go-to-page', page)"
        >
          {{ page }}
        </button>
        <span v-else class="pagination-ellipsis">...</span>
      </template>
      
      <button 
        :disabled="!hasNextPage" 
        @click="$emit('go-to-page', currentPage + 1)"
        class="pagination-btn"
        title="Próxima página"
      >
        ▶
      </button>
      
      <button 
        :disabled="!hasNextPage" 
        @click="$emit('go-to-page', totalPages)"
        class="pagination-btn"
        title="Última página"
      >
        ⏭
      </button>
    </div>
    
    <div class="pagination-size" v-if="showPageSizeSelector">
      <label for="page-size">Itens por página:</label>
      <select 
        id="page-size"
        :value="pageSize" 
        @change="$emit('change-page-size', parseInt(($event.target as HTMLSelectElement).value))"
        class="page-size-select"
      >
        <option value="5">5</option>
        <option value="10">10</option>
        <option value="20">20</option>
        <option value="50">50</option>
        <option value="100">100</option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  currentPage: number
  totalPages: number
  totalItems: number
  pageSize: number
  showPageSizeSelector?: boolean
  maxVisiblePages?: number
}

const props = withDefaults(defineProps<Props>(), {
  showPageSizeSelector: true,
  maxVisiblePages: 5
})

const emit = defineEmits<{
  'go-to-page': [page: number]
  'change-page-size': [size: number]
}>()

const hasPreviousPage = computed(() => props.currentPage > 1)
const hasNextPage = computed(() => props.currentPage < props.totalPages)

// Calcular páginas visíveis
const visiblePages = computed(() => {
  const { currentPage, totalPages, maxVisiblePages } = props
  
  if (totalPages <= maxVisiblePages) {
    return Array.from({ length: totalPages }, (_, i) => i + 1)
  }
  
  const half = Math.floor(maxVisiblePages / 2)
  let start = Math.max(1, currentPage - half)
  let end = Math.min(totalPages, start + maxVisiblePages - 1)
  
  // Ajustar início se estivermos no final
  if (end - start + 1 < maxVisiblePages) {
    start = Math.max(1, end - maxVisiblePages + 1)
  }
  
  const pages: (number | string)[] = []
  
  if (start > 1) {
    pages.push(1)
    if (start > 2) {
      pages.push('...')
    }
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  if (end < totalPages) {
    if (end < totalPages - 1) {
      pages.push('...')
    }
    pages.push(totalPages)
  }
  
  return pages
})
</script>

<style scoped>
.pagination-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-background);
  border-radius: 8px;
  margin-top: 1rem;
}

.pagination-info {
  font-size: 0.9rem;
  color: #6c757d;
}

.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.pagination-btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid #dee2e6;
  background: var(--color-background);
  color: var(--color-text);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  min-width: 2.5rem;
  text-align: center;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--color-background-hover);
  border-color: var(--color-border-hover);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.pagination-btn.page-number {
  font-weight: 500;
}

.pagination-ellipsis {
  padding: 0.5rem;
  color: #6c757d;
  font-weight: bold;
}

.pagination-size {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.pagination-size label {
  color: #6c757d;
  font-weight: 500;
}

.page-size-select {
  padding: 0.375rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background: white;
  color: #495057;
  font-size: 0.875rem;
}

.page-size-select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

@media (max-width: 768px) {
  .pagination-controls {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .pagination-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .pagination-size {
    order: -1;
  }
}
</style>
