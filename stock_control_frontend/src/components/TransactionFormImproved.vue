<!-- TransactionFormImproved.vue - Formulário de transação com novo sistema de UX -->
<template>
  <div class="transaction-form">
    <form @submit.prevent="handleSubmit" class="form">
      <div class="form-header">
        <h3>{{ isEditMode ? 'Editar Transação' : 'Nova Transação' }}</h3>
      </div>

      <div class="form-fields">
        <!-- Tipo de Transação -->
        <FormField
          v-model="fields.isEntry.value"
          label="Tipo de Transação"
          type="select"
          :options="transactionTypeOptions"
          :rules="[validationRules.required()]"
          @validate="(isValid, error) => handleFieldValidation('isEntry', isValid, error)"
        />

        <!-- Fornecedor (apenas para entradas) -->
        <FormField
          v-if="fields.isEntry.value === 'true'"
          v-model="supplierSearch"
          label="Fornecedor"
          type="text"
          placeholder="Digite o nome do fornecedor"
          :loading="supplierLoading"
          :suggestions="supplierSuggestions"
          :show-suggestions="showSupplierSuggestions"
          suggestion-key="codFornecedor"
          suggestion-label="nomeFornecedor"
          :rules="[validationRules.required('Selecione um fornecedor')]"
          @validate="(isValid, error) => handleFieldValidation('supplierId', isValid, error)"
          @search="handleSupplierSearch"
          @select-suggestion="selectSupplier"
        />

        <!-- Número da NF (apenas para entradas) -->
        <FormField
          v-if="fields.isEntry.value === 'true' && !isEditMode"
          v-model="fields.codNf.value"
          label="Número da NF"
          type="text"
          placeholder="Digite o número da NF"
          :rules="[
            validationRules.required('Informe o número da NF'),
            validationRules.pattern(/^\d+$/, 'Apenas números são permitidos')
          ]"
          @validate="(isValid, error) => handleFieldValidation('codNf', isValid, error)"
        />

        <!-- Produto -->
        <FormField
          v-model="productSearch"
          label="Produto"
          type="text"
          placeholder="Digite o SKU ou nome do produto"
          :loading="productLoading"
          :suggestions="productSuggestions"
          :show-suggestions="showProductSuggestions"
          suggestion-key="codSku"
          suggestion-label="descricaoItem"
          :rules="[validationRules.required('Selecione um produto')]"
          @validate="(isValid, error) => handleFieldValidation('sku', isValid, error)"
          @search="handleProductSearch"
          @select-suggestion="selectProduct"
        >
          <template #suggestion="{ suggestion }">
            <strong>{{ suggestion.codSku }}</strong> - {{ suggestion.descricaoItem }}
          </template>
        </FormField>

        <!-- Quantidade -->
        <FormField
          v-model="fields.quantity.value"
          label="Quantidade"
          type="text"
          placeholder="Digite a quantidade (ex: 10,5)"
          :rules="[
            validationRules.required('Informe a quantidade'),
            (value) => {
              const num = parseBrazilianNumber(value);
              return num > 0 || 'A quantidade deve ser positiva';
            }
          ]"
          @validate="(isValid, error) => handleFieldValidation('quantity', isValid, error)"
          @input="(value: string | number) => handleBrazilianNumberInput('quantity', value)"
        />

        <!-- Custo Unitário -->
        <FormField
          v-model="fields.unitCost.value"
          label="Custo Unitário"
          type="text"
          :placeholder="isUnitCostDisabled ? 'Custo calculado automaticamente' : 'Digite o custo unitário (ex: 15,99)'"
          :disabled="isUnitCostDisabled"
          :rules="[
            validationRules.required('Informe o custo unitário'),
            (value) => {
              const num = parseBrazilianNumber(value);
              return num > 0 || 'O custo deve ser positivo';
            }
          ]"
          @validate="(isValid, error) => handleFieldValidation('unitCost', isValid, error)"
          @input="(value: string | number) => handleBrazilianNumberInput('unitCost', value)"
        >
          <template #append>
            <LoadingButton
              v-if="fields.isEntry.value === 'true' && fields.sku.value"
              :loading="loadingCost"
              variant="secondary"
              size="small"
              @click="suggestLastCost"
            >
              Sugerir último
            </LoadingButton>
          </template>
        </FormField>
        
        <!-- Texto explicativo para saídas -->
        <div v-if="isUnitCostDisabled" class="field-help-text">
          <svg class="info-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
          </svg>
          <span>Para saídas, o custo unitário é calculado automaticamente baseado no custo médio do estoque.</span>
        </div>

        <!-- Total -->
        <div class="form-field">
          <label class="form-field__label">Total</label>
          <div class="total-display">
            {{ formattedTotalCost }}
          </div>
        </div>
      </div>

      <div class="form-actions">
        <LoadingButton
          variant="secondary"
          @click="handleCancel"
        >
          Cancelar
        </LoadingButton>
        
        <LoadingButton
          type="submit"
          :loading="submitting"
          variant="primary"
        >
          {{ isEditMode ? 'Atualizar' : 'Salvar' }} Transação
        </LoadingButton>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useFormValidation, validationRules } from '@/composables/useFormValidation';
import { useLoading } from '@/composables/useLoading';
import { useErrorHandler } from '@/composables/useApiError';
import FormField from './FormField.vue';
import LoadingButton from './LoadingButton.vue';
import { transactionService } from '@/services/transactionService';
import { supplierService } from '@/services/supplierService';
import { itemService } from '@/services/itemService';
import { stockCostService } from '@/services/stockCostService';
import { useAuthStore } from '@/stores/auth';
import type { TransactionForm as TxFormType } from '@/types/transaction';
import api from '@/types/api';
import { getCurrentISODate } from '@/utils/date';

// Props
const props = defineProps<{
  transaction?: any; // Para edição
}>();

// Emits
const emit = defineEmits<{
  (e: 'submit', transaction: TxFormType): void;
  (e: 'cancel'): void;
}>();

// Composables
const { handleError, handleSuccess } = useErrorHandler();
const { loading: submitting, withLoading } = useLoading();
const { loading: supplierLoading } = useLoading();
const { loading: productLoading } = useLoading();
const { loading: loadingCost } = useLoading();

// Form validation
const {
  fields,
  errors,
  isValid,
  setFieldValue,
  validateForm,
  getFormData,
  resetForm,
} = useFormValidation({
  isEntry: 'true',
  supplierId: '',
  codNf: '',
  sku: '',
  quantity: '',
  unitCost: '',
});

// Estado do formulário
const isEditMode = ref(!!props.transaction);
const supplierSuggestions = ref<any[]>([]);
const productSuggestions = ref<any[]>([]);
const showSupplierSuggestions = ref(false);
const showProductSuggestions = ref(false);
const supplierSearch = ref('');
const productSearch = ref('');

// Opções do tipo de transação
const transactionTypeOptions = [
  { value: 'true', label: 'Entrada' },
  { value: 'false', label: 'Saída' },
];

// Computed
const formData = computed(() => getFormData());

const formattedTotalCost = computed(() => {
  // Protege contra valores vazios para evitar efeitos colaterais em outros campos
  const quantityStr = String(fields.quantity.value || '0');
  const unitCostStr = String(fields.unitCost.value || '0');
  
  const quantity = parseBrazilianNumber(quantityStr);
  const unitCost = parseBrazilianNumber(unitCostStr);
  const total = quantity * unitCost;
  return total > 0 ? `R$ ${total.toFixed(2).replace('.', ',')}` : 'R$ 0,00';
});

// Computed para controlar se o campo de custo unitário deve estar desabilitado
const isUnitCostDisabled = computed(() => {
  return fields.isEntry.value === 'false'; // Desabilitado para saídas
});

// Watchers
watch(() => fields.isEntry.value, (newValue, oldValue) => {
  // Só executa se realmente mudou de entrada para saída
  if (newValue === 'false' && oldValue === 'true') {
    // Proteção adicional: só limpa se não estivermos em modo de inicialização
    if (oldValue !== undefined) {
      setFieldValue('supplierId', '');
      setFieldValue('codNf', '');
    }
  }
});

watch(() => fields.sku.value, (newValue) => {
  if (newValue && fields.isEntry.value === 'false') {
    // Para saídas, sugere o custo médio automaticamente
    getAverageCost(newValue);
  }
});

// Métodos
const handleFieldValidation = (fieldName: string, isValid: boolean, error?: string) => {
  // Lógica adicional de validação se necessário
};

// Handler para campos numéricos brasileiros
const handleBrazilianNumberInput = (fieldName: string, value: string | number) => {
  // Proteção contra valores vazios que possam causar efeitos colaterais
  if (value === null || value === undefined) return;
  
  // Se for o campo unitCost e estiver desabilitado, não processa o input
  if (fieldName === 'unitCost' && isUnitCostDisabled.value) return;
  
  const formattedValue = formatBrazilianNumber(String(value));
  
  // Só atualiza o campo se realmente mudou de valor
  if (fields[fieldName].value !== formattedValue) {
    setFieldValue(fieldName, formattedValue);
  }
};

// Função para formatar número brasileiro (vírgula como separador decimal)
const formatBrazilianNumber = (value: string): string => {
  // Remove caracteres não numéricos exceto vírgula
  const cleanValue = value.replace(/[^\d,]/g, '');
  
  // Se há vírgula, mantém apenas a primeira
  const parts = cleanValue.split(',');
  if (parts.length > 2) {
    return parts[0] + ',' + parts.slice(1).join('');
  }
  
  return cleanValue;
};

// Função para converter número brasileiro para formato americano
const parseBrazilianNumber = (value: string): number => {
  if (!value) return 0;
  // Substitui vírgula por ponto para parseFloat
  const americanFormat = value.replace(',', '.');
  return parseFloat(americanFormat) || 0;
};

const handleSupplierSearch = async (query: string) => {
  if (!query || query.length < 2) {
    supplierSuggestions.value = [];
    showSupplierSuggestions.value = false;
    return;
  }
  
  try {
    await withLoading(async () => {
      const results = await supplierService.searchSuppliers(query);
      supplierSuggestions.value = results.filter(s => s.active);
      showSupplierSuggestions.value = true;
    }, 'supplierLoading');
  } catch (error) {
    console.error('Erro ao buscar fornecedores:', error);
    supplierSuggestions.value = [];
  }
};

const selectSupplier = (supplier: any) => {
  setFieldValue('supplierId', supplier.codFornecedor);
  supplierSearch.value = supplier.nomeFornecedor;
  supplierSuggestions.value = [];
  showSupplierSuggestions.value = false;
};

const handleProductSearch = async (query: string) => {
  if (!query || query.length < 2) {
    productSuggestions.value = [];
    showProductSuggestions.value = false;
    return;
  }
  
  try {
    await withLoading(async () => {
      const { data } = await api.get(`/api/v1/itens/?search=${query}`);
      productSuggestions.value = data.results || [];
      showProductSuggestions.value = true;
    }, 'productLoading');
  } catch (error) {
    console.error('Erro ao buscar produtos:', error);
    productSuggestions.value = [];
  }
};

const selectProduct = (product: any) => {
  setFieldValue('sku', product.codSku);
  productSearch.value = `${product.codSku} - ${product.descricaoItem}`;
  productSuggestions.value = [];
  showProductSuggestions.value = false;
  
  // Se for saída, busca o custo médio
  if (fields.isEntry.value === 'false') {
    getAverageCost(product.codSku);
  }
};

const suggestLastCost = async () => {
  if (!fields.sku.value) return;
  
  try {
    await withLoading(async () => {
      const today = getCurrentISODate();
      const cost = await stockCostService.getStockCosts(1, { 
        stockDate: today, 
        sku: fields.sku.value 
      });
      
      if (cost.results.length > 0) {
        // Converte para formato brasileiro
        const lastCost = cost.results[0].lastEntryCost;
        setFieldValue('unitCost', lastCost.toString().replace('.', ','));
        handleSuccess('Custo sugerido', 'Último custo de entrada aplicado');
      } else {
        handleError('Nenhum custo encontrado', 'Não foi possível encontrar o último custo para este produto');
      }
    }, 'loadingCost');
  } catch (error) {
    handleError(error, 'Erro ao buscar custo');
  }
};

const getAverageCost = async (sku: string) => {
  try {
    // Busca o custo médio através do endpoint de custos de estoque
    const today = new Date().toISOString().split('T')[0];
    const costData = await stockCostService.getStockCosts(1, { 
      stockDate: today, 
      sku: sku 
    });
    
    if (costData.results.length > 0) {
      // Converte para formato brasileiro
      const cost = costData.results[0].unitCost;
      setFieldValue('unitCost', cost.toString().replace('.', ','));
    }
  } catch (error) {
    console.error('Erro ao buscar custo médio:', error);
  }
};

const handleSubmit = async () => {
  if (!validateForm()) {
    handleError('Formulário inválido', 'Por favor, corrija os erros antes de continuar');
    return;
  }

  try {
    await withLoading(async () => {
      const authStore = useAuthStore();
      
      if (!authStore.user?.id) {
        handleError('Usuário não autenticado', 'Por favor, faça login novamente');
        return;
      }

      // Busca informações do usuário
      const currentUserInfo = await transactionService.getCurrentUserInventoryInfo();
      
      if (!currentUserInfo || !currentUserInfo.id) {
        handleError('Erro de configuração', 'Não foi possível associar sua conta a um usuário do sistema');
        return;
      }

      const isEntry = fields.isEntry.value === 'true';
      
      if (isEntry) {
        // Validações específicas para entrada
        if (!fields.supplierId.value) {
          handleError('Fornecedor obrigatório', 'Selecione um fornecedor para a entrada');
          return;
        }
        
        if (!fields.codNf.value) {
          handleError('NF obrigatória', 'Informe o número da NF');
          return;
        }

        // Verifica se já existe entrada com mesma NF e fornecedor
        if (!isEditMode.value) {
          const existing = await transactionService.getTransactions({
            notaFiscal: fields.codNf.value
          });
          
          if (existing.results.length > 0) {
            handleError('NF duplicada', 'Já existe uma entrada com a mesma NF e fornecedor');
            return;
          }
        }

        // Cria transação de entrada
        await transactionService.createEntradaTransaction(
          fields.sku.value,
          parseBrazilianNumber(fields.quantity.value),
          parseBrazilianNumber(fields.unitCost.value).toString(),
          currentUserInfo.id,
          fields.codNf.value,
          parseInt(fields.supplierId.value)
        );
      } else {
        // Cria transação de saída
        await transactionService.createSaidaTransaction(
          fields.sku.value,
          parseBrazilianNumber(fields.quantity.value),
          parseBrazilianNumber(fields.unitCost.value).toString(),
          currentUserInfo.id
        );
      }

      emit('submit', getFormData() as TxFormType);
      resetForm();
    });
  } catch (error) {
    handleError(error, 'Erro ao salvar transação');
  }
};

const handleCancel = () => {
  emit('cancel');
};

// Inicialização
onMounted(() => {
  if (props.transaction) {
    // Preenche o formulário com dados da transação para edição
    setFieldValue('isEntry', props.transaction.transactionType === 'entrada' ? 'true' : 'false');
    setFieldValue('sku', props.transaction.sku);
    setFieldValue('quantity', props.transaction.quantity);
    setFieldValue('unitCost', props.transaction.unitCost);
    
    if (props.transaction.transactionType === 'entrada' && props.transaction.notaFiscal) {
      setFieldValue('codNf', props.transaction.notaFiscal);
    }
  }
});
</script>

<style scoped>
.transaction-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
}

.form {
  /*background: white;*/
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.form-header {
  margin-bottom: 24px;
  text-align: center;
}

.form-header h3 {
  margin: 0;
  /*color: #1f2937;*/
  font-size: 20px;
  font-weight: 600;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 24px;
}

.total-display {
  padding: 12px;
  /*background: #f3f4f6;*/
  border-radius: 6px;
  font-size: 18px;
  font-weight: 600;
  /*color: #1f2937;*/
  text-align: center;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}


@media (max-width: 640px) {
  .transaction-form {
    padding: 16px;
  }
  
  .form {
    padding: 16px;
  }
  
  .form-actions {
    flex-direction: column;
  }
}

.field-help-text {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 12px;
  /*background: #f0f9ff;*/
  border: 1px solid #bae6fd;
  border-radius: 6px;
  font-size: 14px;
  color: #0369a1;
}

.info-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: #0284c7;
}
</style>
