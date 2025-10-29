<!-- LoadingButton.vue - Botão com estado de carregamento -->
<template>
  <button
    :type="type"
    :class="[
      'loading-button',
      `loading-button--${variant}`,
      `loading-button--${size}`,
      {
        'loading-button--loading': loading,
        'loading-button--disabled': disabled || loading
      }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <LoadingSpinner
      v-if="loading"
      size="small"
      class="loading-button__spinner"
    />
    <span :class="{ 'loading-button__text--hidden': loading }">
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
import LoadingSpinner from './LoadingSpinner.vue';

interface Props {
  loading?: boolean;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning';
  size?: 'small' | 'medium' | 'large';
  type?: 'button' | 'submit' | 'reset';
}

interface Emits {
  (e: 'click', event: MouseEvent): void;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  disabled: false,
  variant: 'primary',
  size: 'medium',
  type: 'button',
});

const emit = defineEmits<Emits>();

function handleClick(event: MouseEvent) {
  if (!props.loading && !props.disabled) {
    emit('click', event);
  }
}
</script>

<style scoped>
.loading-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  outline: none;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.loading-button:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Variantes */
.loading-button--primary {
  background: #3b82f6;
  color: white;
}

.loading-button--primary:hover:not(.loading-button--disabled) {
  background: #2563eb;
}

.loading-button--secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.loading-button--secondary:hover:not(.loading-button--disabled) {
  background: #e5e7eb;
}

.loading-button--danger {
  background: #ef4444;
  color: white;
}

.loading-button--danger:hover:not(.loading-button--disabled) {
  background: #dc2626;
}

.loading-button--success {
  background: #10b981;
  color: white;
}

.loading-button--success:hover:not(.loading-button--disabled) {
  background: #059669;
}

.loading-button--warning {
  background: #f59e0b;
  color: white;
}

.loading-button--warning:hover:not(.loading-button--disabled) {
  background: #d97706;
}

/* Tamanhos */
.loading-button--small {
  padding: 6px 12px;
  font-size: 12px;
  min-height: 32px;
}

.loading-button--medium {
  padding: 8px 16px;
  font-size: 14px;
  min-height: 40px;
}

.loading-button--large {
  padding: 12px 24px;
  font-size: 16px;
  min-height: 48px;
}

/* Estados */
.loading-button--disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-button--loading {
  cursor: wait;
}

.loading-button__spinner {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}

.loading-button__text--hidden {
  opacity: 0;
}

/* Animações */
.loading-button {
  transform: translateY(0);
}

.loading-button:active:not(.loading-button--disabled) {
  transform: translateY(1px);
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
}
</style>
