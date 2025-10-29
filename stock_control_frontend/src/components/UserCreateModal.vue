<!-- UserCreateModal.vue - Refatorado com novo sistema UX -->
<template>
  <div class="modal-backdrop" @click="handleBackdropClick">
    <div class="modal form-container" @click.stop>
      <div class="modal-header">
        <h2>Criar Novo Usuário</h2>
        <button class="modal-close" @click="$emit('cancel')" aria-label="Fechar">
          <svg viewBox="0 0 24 24" fill="currentColor" class="close-icon">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="form">
        <div class="form-fields">
          <FormField
            v-model="formData.username"
            label="Nome de usuário"
            type="text"
            placeholder="Digite o nome de usuário"
            :rules="[
              validationRules.required('Nome de usuário é obrigatório'),
              validationRules.minLength(3, 'Nome deve ter pelo menos 3 caracteres')
            ]"
            @validate="(isValid, error) => handleFieldValidation('username', isValid, error)"
          />

          <FormField
            v-model="formData.firstName"
            label="Nome"
            type="text"
            placeholder="Digite o nome"
            :rules="[validationRules.required('Nome é obrigatório')]"
            @validate="(isValid, error) => handleFieldValidation('firstName', isValid, error)"
          />

          <FormField
            v-model="formData.lastName"
            label="Sobrenome"
            type="text"
            placeholder="Digite o sobrenome"
            :rules="[validationRules.required('Sobrenome é obrigatório')]"
            @validate="(isValid, error) => handleFieldValidation('lastName', isValid, error)"
          />

          <FormField
            v-model="formData.email"
            label="E-mail"
            type="email"
            placeholder="Digite o e-mail"
            :rules="[
              validationRules.required('E-mail é obrigatório'),
              validationRules.email('E-mail inválido')
            ]"
            @validate="(isValid, error) => handleFieldValidation('email', isValid, error)"
          />

          <FormField
            v-model="formData.password"
            label="Senha"
            type="password"
            placeholder="Digite a senha"
            :rules="[
              validationRules.required('Senha é obrigatória'),
              validationRules.minLength(8, 'Senha deve ter pelo menos 8 caracteres')
            ]"
            @validate="(isValid, error) => handleFieldValidation('password', isValid, error)"
          />

          <FormField
            v-model="formData.password2"
            label="Confirmar Senha"
            type="password"
            placeholder="Confirme a senha"
            :rules="[
              validationRules.required('Confirmação de senha é obrigatória'),
              passwordMatchRule
            ]"
            @validate="(isValid, error) => handleFieldValidation('password2', isValid, error)"
          />

          <div class="form-field">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="formData.isSuperuser"
                class="checkbox-input"
              />
              <span class="checkbox-text">Usuário Master (Admin)</span>
            </label>
          </div>

          <div class="form-field">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="formData.isActive"
                class="checkbox-input"
              />
              <span class="checkbox-text">Usuário Ativo</span>
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
            Criar Usuário
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
import type { CreateUserData } from '@/services/userService';

const emit = defineEmits<{
  (e: 'cancel'): void;
  (e: 'save', userData: CreateUserData): void;
}>();

// Composables
const { handleError, handleSuccess } = useErrorHandler();
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
  username: '',
  email: '',
  password: '',
  password2: '',
  firstName: '',
  lastName: '',
  isActive: true,
  isSuperuser: false,
  permissionsList: ['dashboard']
});

// Computed
const formData = computed(() => getFormData());

// Regra customizada para validação de senha
const passwordMatchRule = computed(() => 
  validationRules.custom((value: string) => {
    if (value !== formData.value.password) {
      return 'As senhas não coincidem';
    }
    return true;
  })
);

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
      const userData: CreateUserData = {
        ...formData.value,
        permissionsList: ['dashboard'] // Permissão básica
      };
      
      emit('save', userData);
    });
  } catch (error) {
    handleError(error, 'Erro ao criar usuário');
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
  /* background: white; */
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
  /*color: #1f2937;*/
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