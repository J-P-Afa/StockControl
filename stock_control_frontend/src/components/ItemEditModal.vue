<!-- ItemEditModal.vue - Refatorado com novo sistema UX -->
<template>
  <div class="modal-backdrop" @click="handleBackdropClick">
    <div class="modal form-container" @click.stop>
      <div class="modal-header">
        <h2>{{ item.codSku ? 'Editar Item' : 'Cadastrar Novo Item' }}</h2>
        <button class="modal-close" @click="$emit('cancel')" aria-label="Fechar">
          <svg viewBox="0 0 24 24" fill="currentColor" class="close-icon">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="form">
        <div class="form-fields">
          <FormField
            v-model="formData.codSku"
            label="SKU"
            type="text"
            placeholder="Digite o SKU do item"
            :disabled="!!item.codSku"
            :rules="[
              validationRules.required('SKU é obrigatório'),
              validationRules.minLength(3, 'SKU deve ter pelo menos 3 caracteres')
            ]"
            @validate="(isValid, error) => handleFieldValidation('codSku', isValid, error)"
          />

          <FormField
            v-model="formData.descricaoItem"
            label="Descrição"
            type="text"
            placeholder="Digite a descrição do item"
            :rules="[
              validationRules.required('Descrição é obrigatória'),
              validationRules.minLength(3, 'Descrição deve ter pelo menos 3 caracteres')
            ]"
            @validate="(isValid, error) => handleFieldValidation('descricaoItem', isValid, error)"
          />

          <FormField
            v-model="formData.unidMedida"
            label="Unidade de Medida"
            type="text"
            placeholder="Ex: UN, KG, L, etc."
            :rules="[
              validationRules.required('Unidade de medida é obrigatória'),
              validationRules.minLength(2, 'Unidade deve ter pelo menos 2 caracteres')
            ]"
            @validate="(isValid, error) => handleFieldValidation('unidMedida', isValid, error)"
          />

          <div class="form-field">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="formData.active"
                class="checkbox-input"
              />
              <span class="checkbox-text">Item ativo</span>
            </label>
          </div>
        </div>

        <div class="form-actions">
          <LoadingButton
            variant="secondary"
            @click="$emit('cancel')"
          >
            Cancelar
          </LoadingButton>
          
          <LoadingButton
            type="submit"
            :loading="submitting"
            variant="primary"
          >
            {{ item.codSku ? 'Atualizar' : 'Criar' }} Item
          </LoadingButton>
        </div>
      </form>
    </div>
  </div>
</template>
  
<script setup lang="ts">
import { computed } from 'vue';
import { useFormValidation, validationRules } from '@/composables/useFormValidation';
import { useLoading } from '@/composables/useLoading';
import { useErrorHandler } from '@/composables/useApiError';
import FormField from './FormField.vue';
import LoadingButton from './LoadingButton.vue';
import type { Item } from '@/services/itemService';

const props = defineProps<{
  item: Item;
}>();

const emit = defineEmits<{
  (e: 'cancel'): void;
  (e: 'save', updated: Item): void;
}>();

// Composables
const { handleError, handleValidationError, handleSuccess } = useErrorHandler();
const { loading: submitting, withLoading } = useLoading();

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
  codSku: props.item.codSku || '',
  descricaoItem: props.item.descricaoItem || '',
  unidMedida: props.item.unidMedida || '',
  active: props.item.active ?? true,
});

// Computed
const formData = computed(() => getFormData());

// Métodos
const handleFieldValidation = (fieldName: string, isValid: boolean, error?: string) => {
  // Lógica adicional de validação se necessário
};

const handleSubmit = async () => {
  if (!validateForm()) {
    handleError('Formulário inválido', 'Por favor, corrija os erros antes de continuar');
    return;
  }

  try {
    await withLoading(async () => {
      const itemData: Item = {
        ...formData.value,
        codSku: formData.value.codSku || props.item.codSku
      };
      
      emit('save', itemData);
    });
  } catch (error) {
    // Usa o novo método para erros de validação
    handleValidationError(error, 'Erro ao salvar item');
  }
};

const handleBackdropClick = () => {
  emit('cancel');
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  /*background: white;*/
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  /* color: #1f2937; */
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  color: #6b7280;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #374151;
}

.close-icon {
  width: 20px;
  height: 20px;
}

.form {
  padding: 0 24px 24px 24px;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 24px;
}

.form-field {
  margin-bottom: 16px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  accent-color: #3b82f6;
}

.checkbox-text {
  user-select: none;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

@media (max-width: 640px) {
  .modal-backdrop {
    padding: 10px;
  }
  
  .modal-header {
    padding: 16px 16px 0 16px;
  }
  
  .form {
    padding: 0 16px 16px 16px;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
  
  