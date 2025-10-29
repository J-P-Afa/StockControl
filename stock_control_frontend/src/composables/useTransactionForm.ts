// composables/useTransactionForm.ts - Lógica para formulário de transações
import { ref, computed, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { transactionService, type FormattedTransaction } from '@/services/transactionService';
import { stockCostService } from '@/services/stockCostService';
import type { TransactionForm } from '@/types/transaction';
import type { Item } from '@/types/item';
import type { Fornecedor } from '@/services/supplierService';
import { getCurrentISODate } from '@/utils/date';
import api from '@/services/api';
import { createLogger } from '@/utils/logger';
import { useFormValidation, validationRules } from '@/composables/useFormValidation';

const logger = createLogger('useTransactionForm');

export function useTransactionForm(initialForm?: Partial<TransactionForm>, transaction?: FormattedTransaction) {
  const authStore = useAuthStore();
  const loading = ref(false);
  const loadingCost = ref(false);
  const isEditMode = ref(!!transaction);

  // Estado do formulário
  const form = ref<TransactionForm>({
    isEntry: true,
    supplierId: undefined,
    supplierName: undefined,
    codNf: '',
    sku: '',
    product: '',
    quantity: 0.0,
    unitCost: 0.0,
    ...initialForm
  });

  // Estado para fornecedor selecionado
  const selectedSupplier = ref<Fornecedor | null>(null);
  
  // Estado para produto selecionado
  const selectedProduct = ref<Item | null>(null);

  // Computed para custo total
  const totalCost = computed(() => form.value.quantity * form.value.unitCost);
  
  const formattedTotalCost = computed(() => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(totalCost.value);
  });

  // Watch para sincronizar fornecedor selecionado
  watch(selectedSupplier, (supplier) => {
    if (supplier) {
      form.value.supplierId = supplier.codFornecedor;
      form.value.supplierName = supplier.nomeFornecedor;
    } else {
      form.value.supplierId = undefined;
      form.value.supplierName = undefined;
    }
  });

  // Watch para sincronizar produto selecionado
  watch(selectedProduct, async (product) => {
    if (product) {
      form.value.sku = product.codSku;
      form.value.product = product.descricaoItem;
      
      // Atualizar custo ao selecionar produto (apenas se não estiver editando)
      if (!isEditMode.value) {
        await updateCostForProduct();
      }
    } else {
      form.value.sku = '';
      form.value.product = '';
    }
  });

  // Watch para mudanças no tipo de transação
  watch(() => form.value.isEntry, async (isEntry) => {
    if (!isEntry) {
      // Reset campos específicos de entrada
      form.value.supplierId = undefined;
      form.value.supplierName = undefined;
      form.value.codNf = '';
      selectedSupplier.value = null;
      
      // Atualiza custo unitário para saída (apenas se não estiver editando)
      if (form.value.sku && !isEditMode.value) {
        await updateUnitCostForOutput();
      }
    }
  });

  // Função helper para garantir booleano
  function ensureBooleanValue(value: any): boolean {
    if (typeof value === 'boolean') return value;
    if (typeof value === 'string') {
      const lowercaseValue = value.toLowerCase();
      return lowercaseValue === 'true' || 
             lowercaseValue === 'entrada' ||
             lowercaseValue.includes('entrada');
    }
    return Boolean(value);
  }

  // Função para calcular unit cost baseado no tipo de transação e produto
  async function calculateUnitCost(transaction?: FormattedTransaction): Promise<number> {
    if (!form.value.sku) return 0;

    // Se estamos editando e temos o unitCost
    if (transaction && transaction.unitCost !== undefined) {
      return transaction.unitCost;
    }

    // Se temos cost e quantity
    if (transaction && transaction.cost !== undefined && transaction.quantity) {
      return transaction.cost / transaction.quantity;
    }

    // Se temos totalCost e quantity
    if (transaction && transaction.totalCost !== undefined && transaction.quantity) {
      return Math.round((transaction.totalCost / transaction.quantity) * 100) / 100;
    }

    // Para novas transações
    return 0;
  }

  // Função para obter custo médio
  async function getAverageCost(sku: string): Promise<number> {
    try {
      loadingCost.value = true;
      
      try {
        const { data } = await api.get(`/api/v1/itens/${sku}/custo-medio/`);
        if (data && data.custoMedio !== undefined) {
          logger.debug('Custo médio obtido da API:', data.custoMedio);
          return data.custoMedio;
        }
      } catch (apiError) {
        logger.error('Erro ao buscar custo médio da API específica:', apiError);
      }

      const response = await stockCostService.getStockCosts(undefined, { sku });
      if (response.results.length > 0) {
        logger.debug('Custo médio obtido do stockCostService:', response.results[0].unitCost);
        return response.results[0].unitCost;
      }
      return 0;
    } catch (error) {
      logger.error('Erro ao buscar custo médio:', error);
      return 0;
    } finally {
      loadingCost.value = false;
    }
  }

  // Função para atualizar custo quando produto é selecionado
  async function updateCostForProduct() {
    if (!form.value.sku || isEditMode.value) return;

    const isEntryBoolean = ensureBooleanValue(form.value.isEntry);
    
    if (!isEntryBoolean) {
      // Para saídas, o custo é sempre o custo médio
      form.value.unitCost = await getAverageCost(form.value.sku);
    } else {
      // Para entradas, preenche com uma sugestão mas permite edição
      const lastEntryCost = await getLastEntryCost(form.value.sku);
      if (lastEntryCost > 0) {
        form.value.unitCost = lastEntryCost;
      }
    }
  }

  // Função para obter custo da última entrada
  async function getLastEntryCost(sku: string): Promise<number> {
    try {
      loadingCost.value = true;
      const today = getCurrentISODate();
      const lastEntryCost = await stockCostService.getStockCosts(today, { sku });
      if (lastEntryCost.results.length > 0) {
        return lastEntryCost.results[0].lastEntryCost;
      }
      return 0;
    } catch (error) {
      logger.error('Erro ao buscar último custo de entrada:', error);
      return 0;
    } finally {
      loadingCost.value = false;
    }
  }

  // Função para atualizar custo unitário para saída
  async function updateUnitCostForOutput() {
    if (form.value.sku) {
      form.value.unitCost = await getAverageCost(form.value.sku);
    }
  }

  // Função para sugerir último custo (entrada)
  async function suggestLastCost() {
    if (form.value.sku) {
      form.value.unitCost = await getLastEntryCost(form.value.sku);
    }
  }

  // Setup de validação
  const validation = useFormValidation({
    sku: form.value.sku,
    quantity: form.value.quantity,
    unitCost: form.value.unitCost,
    supplierId: form.value.supplierId,
    codNf: form.value.codNf
  });

  // Configurar regras de validação
  validation.setFieldRules('sku', [
    validationRules.required('Por favor, selecione um produto.')
  ]);
  
  validation.setFieldRules('quantity', [
    validationRules.required('A quantidade é obrigatória.'),
    validationRules.positive('A quantidade deve ser maior que zero.')
  ]);
  
  validation.setFieldRules('unitCost', [
    validationRules.required('O custo unitário é obrigatório.'),
    validationRules.positive('O custo unitário deve ser maior que zero.')
  ]);

  // Sincronizar valores do formulário com validação
  watch(() => form.value.sku, (value) => validation.setFieldValue('sku', value));
  watch(() => form.value.quantity, (value) => validation.setFieldValue('quantity', value));
  watch(() => form.value.unitCost, (value) => validation.setFieldValue('unitCost', value));
  watch(() => form.value.supplierId, (value) => validation.setFieldValue('supplierId', value));
  watch(() => form.value.codNf, (value) => validation.setFieldValue('codNf', value));
  
  // Atualizar regras quando tipo de transação muda
  watch(() => form.value.isEntry, (isEntry) => {
    if (isEntry) {
      validation.setFieldRules('supplierId', [
        validationRules.required('Por favor, selecione um fornecedor.')
      ]);
      validation.setFieldRules('codNf', [
        validationRules.required('Por favor, informe o número da NF.')
      ]);
    } else {
      validation.setFieldRules('supplierId', []);
      validation.setFieldRules('codNf', []);
    }
  });

  // Função para validar se a operação é válida
  function validateForm(): string | null {
    if (!validation.validateForm()) {
      const firstError = Object.values(validation.errors.value)[0];
      return firstError || 'Por favor, corrija os erros do formulário.';
    }
    return null;
  }

  // Função para resetar o formulário
  function resetForm() {
    form.value = {
      isEntry: true,
      supplierId: undefined,
      supplierName: undefined,
      codNf: '',
      sku: '',
      product: '',
      quantity: 0.0,
      unitCost: 0.0,
    };
    selectedSupplier.value = null;
    selectedProduct.value = null;
  }

  // Função para submeter o formulário
  async function submitForm(): Promise<void> {
    const validationError = validateForm();
    if (validationError) {
      throw new Error(validationError);
    }

    loading.value = true;
    try {
      const currentUserInfo = await transactionService.getCurrentUserInventoryInfo();
      
      if (!currentUserInfo || !currentUserInfo.id) {
        throw new Error('Não foi possível associar sua conta a um usuário do sistema.');
      }

      if (form.value.isEntry) {
        await transactionService.createEntradaTransaction(
          form.value.sku,
          form.value.quantity,
          form.value.unitCost.toString(),
          currentUserInfo.id,
          form.value.codNf!,
          form.value.supplierId!
        );
      } else {
        await transactionService.createSaidaTransaction(
          form.value.sku,
          form.value.quantity,
          form.value.unitCost.toString(),
          currentUserInfo.id
        );
      }
    } finally {
      loading.value = false;
    }
  }

  return {
    form,
    selectedSupplier,
    selectedProduct,
    loading,
    loadingCost,
    isEditMode,
    totalCost,
    formattedTotalCost,
    calculateUnitCost,
    getAverageCost,
    getLastEntryCost,
    updateCostForProduct,
    suggestLastCost,
    validation,
    validateForm,
    resetForm,
    submitForm,
    ensureBooleanValue
  };
}
