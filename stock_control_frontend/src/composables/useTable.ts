// useTable.ts - Composable para gerenciar tabelas com ordenação e filtros
import { ref, computed } from 'vue';
import type { Ref } from 'vue';
import type { SortDirection } from '@/types/common';

/**
 * Definição de uma coluna de tabela
 * 
 * @template T - Tipo do objeto da linha
 */
export interface ColumnDef<T> {
  /** Chave da propriedade no objeto */
  key: keyof T;
  /** Label exibida no cabeçalho da coluna */
  label: string;
  /** Se a coluna pode ser ordenada */
  sortable?: boolean;
  /** Função customizada para ordenação (opcional) */
  sortFn?: (a: T, b: T, order: SortDirection) => number;
}

/**
 * Tipo de comparação para valores primitivos
 */
type Comparable = string | number | boolean | Date;

/**
 * Composable para gerenciar estado de tabelas com ordenação e filtros
 * 
 * @template T - Tipo do objeto da linha
 * @param rows - Ref com array de dados da tabela
 * @param columns - Definições das colunas
 * @param initialFilters - Filtros iniciais (opcional)
 * 
 * @returns Objeto com estado e métodos para gerenciar a tabela
 * 
 * @example
 * ```ts
 * const users = ref<User[]>([...]);
 * const columns: ColumnDef<User>[] = [
 *   { key: 'name', label: 'Nome', sortable: true },
 *   { key: 'email', label: 'Email', sortable: true }
 * ];
 * 
 * const table = useTable(users, columns);
 * ```
 */
export function useTable<T extends Record<string, any>>(
  rows: Ref<T[]>,
  columns: ColumnDef<T>[],
  initialFilters: Record<string, string> = {}
) {
  const sortKey = ref<keyof T | null>(null);
  const sortOrder = ref<SortDirection>('asc');
  const filters = ref({ ...initialFilters });

  /**
   * Compara dois valores primitivos considerando a ordem (asc/desc)
   */
  const compareValues = (a: Comparable, b: Comparable, order: SortDirection): number => {
    // Normaliza valores para comparação
    const normalizedA = a?.toString().toLowerCase() ?? '';
    const normalizedB = b?.toString().toLowerCase() ?? '';
    
    // Compara valores
    if (normalizedA < normalizedB) return order === 'asc' ? -1 : 1;
    if (normalizedA > normalizedB) return order === 'asc' ? 1 : -1;
    return 0;
  };

  /**
   * Aplica filtros aos dados
   */
  const applyFilters = (data: T[]): T[] => {
    return data.filter(item => {
      return Object.entries(filters.value).every(([field, substr]) => {
        if (!substr) return true;
        
        const value = item[field as keyof T];
        return String(value).toLowerCase().includes(substr.toLowerCase());
      });
    });
  };

  /**
   * Aplica ordenação aos dados
   */
  const applySort = (data: T[]): T[] => {
    if (!sortKey.value) return data;

    const column = columns.find(c => c.key === sortKey.value);
    if (!column?.sortable) return data;

    return [...data].sort((a, b) => {
      // Usa função customizada se fornecida
      if (column.sortFn) {
        return column.sortFn(a, b, sortOrder.value);
      }

      // Usa comparação padrão
      const aValue = a[sortKey.value!] as Comparable;
      const bValue = b[sortKey.value!] as Comparable;
      return compareValues(aValue, bValue, sortOrder.value);
    });
  };

  /**
   * Dados filtrados e ordenados
   */
  const filteredAndSorted = computed(() => {
    let result = [...rows.value];
    
    // Aplica filtros
    result = applyFilters(result);
    
    // Aplica ordenação
    result = applySort(result);
    
    return result;
  });

  /**
   * Define a coluna de ordenação
   * Se clicar na mesma coluna, inverte a ordem
   * 
   * @param key - Chave da coluna para ordenar
   */
  const setSort = (key: keyof T): void => {
    if (sortKey.value === key) {
      // Inverte a ordem se for a mesma coluna
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
    } else {
      // Nova coluna, começa com ordem ascendente
      sortKey.value = key;
      sortOrder.value = 'asc';
    }
  };

  /**
   * Define o valor de um filtro
   * 
   * @param field - Campo a ser filtrado
   * @param value - Valor do filtro
   */
  const setFilter = (field: string, value: string): void => {
    filters.value[field] = value;
  };

  /**
   * Limpa todos os filtros
   */
  const clearFilters = (): void => {
    filters.value = { ...initialFilters };
  };

  /**
   * Limpa a ordenação
   */
  const clearSort = (): void => {
    sortKey.value = null;
    sortOrder.value = 'asc';
  };

  /**
   * Reseta tabela ao estado inicial
   */
  const reset = (): void => {
    clearFilters();
    clearSort();
  };

  return {
    // Estado
    sortKey,
    sortOrder,
    filters,
    data: filteredAndSorted,
    
    // Métodos
    setSort,
    setFilter,
    clearFilters,
    clearSort,
    reset,
  };
}
