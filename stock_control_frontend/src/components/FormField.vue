<!-- FormField.vue - Campo de formulário com validação e feedback -->
<template>
  <div class="form-field">
    <label 
      v-if="label" 
      :for="fieldId" 
      :class="[
        'form-field__label',
        { 'form-field__label--required': required }
      ]"
    >
      {{ label }}
    </label>
    
    <div class="form-field__input-container">
      <!-- Select field -->
      <select
        v-if="type === 'select'"
        :id="fieldId"
        v-model="inputValue"
        :required="required"
        :disabled="disabled"
        :class="[
          'form-field__select',
          {
            'form-field__select--error': hasError,
            'form-field__select--success': isValid && !hasError,
            'form-field__select--disabled': disabled
          }
        ]"
        @blur="handleBlur"
        @change="handleInput"
        @focus="handleFocus"
      >
        <option value="" disabled>{{ placeholder || 'Selecione uma opção' }}</option>
        <option
          v-for="option in options"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>
      
      <!-- Text/Number input field with autocomplete -->
      <div v-else class="form-field__autocomplete-container">
        <input
          :id="fieldId"
          v-model="inputValue"
          :type="type"
          :placeholder="placeholder"
          :required="required"
          :disabled="disabled"
          :class="[
            'form-field__input',
            {
              'form-field__input--error': hasError,
              'form-field__input--success': isValid && !hasError,
              'form-field__input--disabled': disabled
            }
          ]"
          @blur="handleBlur"
          @input="handleInput"
          @focus="handleFocus"
          @keydown="handleKeydown"
        />
        
        <!-- Autocomplete suggestions -->
        <div 
          v-if="showSuggestions && suggestions.length > 0" 
          class="form-field__suggestions"
        >
          <div
            v-for="(suggestion, index) in suggestions"
            :key="getSuggestionKey(suggestion, index)"
            :class="[
              'form-field__suggestion-item',
              { 'form-field__suggestion-item--active': selectedSuggestionIndex === index }
            ]"
            @click="selectSuggestion(suggestion)"
            @mouseover="selectedSuggestionIndex = index"
          >
            <slot name="suggestion" :suggestion="suggestion" :index="index">
              {{ getSuggestionLabel(suggestion) }}
            </slot>
          </div>
        </div>
      </div>
      
      <div v-if="loading" class="form-field__loading">
        <LoadingSpinner size="small" />
      </div>
      
      <div v-if="hasError" class="form-field__error-icon">
        <svg viewBox="0 0 24 24" fill="currentColor" class="error-icon">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </div>
      
      <div v-if="isValid && !hasError" class="form-field__success-icon">
        <svg viewBox="0 0 24 24" fill="currentColor" class="success-icon">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        </svg>
      </div>
    </div>
    
    <div v-if="helpText && !hasError" class="form-field__help">
      {{ helpText }}
    </div>
    
    <div v-if="hasError" class="form-field__error">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import LoadingSpinner from './LoadingSpinner.vue';

interface Props {
  modelValue: string | number;
  label?: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  loading?: boolean;
  helpText?: string;
  error?: string;
  rules?: Array<(value: any) => string | boolean>;
  validateOnBlur?: boolean;
  validateOnInput?: boolean;
  options?: Array<{ value: string | number; label: string }>;
  // Autocomplete props
  suggestions?: any[];
  showSuggestions?: boolean;
  suggestionKey?: string;
  suggestionLabel?: string;
  onSearch?: (query: string) => void;
}

interface Emits {
  (e: 'update:modelValue', value: string | number): void;
  (e: 'blur'): void;
  (e: 'focus'): void;
  (e: 'input', value: string | number): void;
  (e: 'validate', isValid: boolean, error?: string): void;
  (e: 'search', query: string): void;
  (e: 'select-suggestion', suggestion: any): void;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false,
  disabled: false,
  loading: false,
  validateOnBlur: true,
  validateOnInput: false,
});

const emit = defineEmits<Emits>();

const fieldId = `field-${Math.random().toString(36).substr(2, 9)}`;
const inputValue = ref(props.modelValue);
const touched = ref(false);
const internalError = ref('');
const selectedSuggestionIndex = ref(-1);

// Computed properties
const hasError = computed(() => !!(props.error || internalError.value));
const errorMessage = computed(() => props.error || internalError.value);
const isValid = computed(() => touched.value && !hasError.value && inputValue.value !== '');

// Watch for external modelValue changes
watch(() => props.modelValue, (newValue) => {
  inputValue.value = newValue;
});

// Watch for internal value changes
watch(inputValue, (newValue) => {
  emit('update:modelValue', newValue);
  
  if (props.validateOnInput && touched.value) {
    validateField();
  }
});

// Validation function
function validateField(): boolean {
  if (!props.rules || props.rules.length === 0) {
    return true;
  }

  for (const rule of props.rules) {
    const result = rule(inputValue.value);
    if (typeof result === 'string') {
      internalError.value = result;
      emit('validate', false, result);
      return false;
    } else if (result === false) {
      internalError.value = 'Valor inválido';
      emit('validate', false, 'Valor inválido');
      return false;
    }
  }

  internalError.value = '';
  emit('validate', true);
  return true;
}

// Event handlers
function handleBlur() {
  touched.value = true;
  if (props.validateOnBlur) {
    validateField();
  }
  emit('blur');
}

function handleFocus() {
  emit('focus');
}

function handleInput() {
  emit('input', inputValue.value);
  
  // Trigger search for autocomplete
  if (props.onSearch && typeof inputValue.value === 'string') {
    emit('search', inputValue.value);
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (!props.showSuggestions || !props.suggestions?.length) return;
  
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      selectedSuggestionIndex.value = Math.min(
        selectedSuggestionIndex.value + 1,
        props.suggestions.length - 1
      );
      break;
    case 'ArrowUp':
      event.preventDefault();
      selectedSuggestionIndex.value = Math.max(selectedSuggestionIndex.value - 1, -1);
      break;
    case 'Enter':
      event.preventDefault();
      if (selectedSuggestionIndex.value >= 0) {
        selectSuggestion(props.suggestions[selectedSuggestionIndex.value]);
      }
      break;
    case 'Escape':
      selectedSuggestionIndex.value = -1;
      break;
  }
}

function selectSuggestion(suggestion: any) {
  const value = props.suggestionKey ? suggestion[props.suggestionKey] : suggestion;
  inputValue.value = value;
  selectedSuggestionIndex.value = -1;
  emit('select-suggestion', suggestion);
}

function getSuggestionKey(suggestion: any, index: number): string {
  if (props.suggestionKey) {
    return String(suggestion[props.suggestionKey]);
  }
  return String(index);
}

function getSuggestionLabel(suggestion: any): string {
  if (props.suggestionLabel) {
    return suggestion[props.suggestionLabel];
  }
  return String(suggestion);
}
</script>

<style scoped>
.form-field {
  margin-bottom: 5px;
}

.form-field__label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  font-weight: 500;
  /*color: #374151;*/
}

.form-field__label--required::after {
  content: ' *';
  color: #ef4444;
}

.form-field__input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.form-field__input {
  width: 100%;
  padding: 5px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: white;
}

.form-field__input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-field__input--error {
  border-color: #ef4444;
}

.form-field__input--error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-field__input--success {
  border-color: #10b981;
}

.form-field__input--success:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-field__input--disabled {
  background-color: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.form-field__select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s ease;
  /*background: white;*/
  cursor: pointer;
}

.form-field__select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-field__select--error {
  border-color: #ef4444;
}

.form-field__select--error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-field__select--success {
  border-color: #10b981;
}

.form-field__select--success:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-field__select--disabled {
  background-color: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.form-field__loading,
.form-field__error-icon,
.form-field__success-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
}

.form-field__error-icon {
  color: #ef4444;
}

.form-field__success-icon {
  color: #10b981;
}

.error-icon,
.success-icon {
  width: 100%;
  height: 100%;
}

.form-field__help {
  margin-top: 4px;
  font-size: 12px;
  /*color: #6b7280;*/
}

.form-field__error {
  margin-top: 4px;
  font-size: 12px;
  color: #ef4444;
  display: flex;
  align-items: center;
  gap: 4px;
}

.form-field__error::before {
  content: '⚠';
  font-size: 12px;
}

.form-field__autocomplete-container {
  position: relative;
}

.form-field__suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--color-background);
  border: 1px solid #d1d5db;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
  margin-top: 2px;
}

.form-field__suggestion-item {
  padding: 5px;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.2s ease;
}

.form-field__suggestion-item:hover,
.form-field__suggestion-item--active {
  background: #3b82f6;
}

.form-field__suggestion-item:last-child {
  border-bottom: none;
}
</style>
