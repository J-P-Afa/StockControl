<template>
  <div class="accessibility-settings">
    <div class="settings-header">
      <h3>Configurações de Acessibilidade</h3>
      <p class="settings-description">
        Personalize a interface para melhorar sua experiência de uso
      </p>
    </div>

    <div class="settings-content">
      <!-- Tamanho da Fonte -->
      <div class="setting-group">
        <label class="setting-label">
          <span class="label-text">Tamanho da Fonte</span>
          <span class="label-description">Ajuste o tamanho do texto para melhor legibilidade</span>
        </label>
        
        <div class="font-size-options">
          <button
            v-for="option in fontSizeOptions"
            :key="option.value"
            :class="[
              'font-size-option',
              { 'active': isFontSize(option.value) }
            ]"
            :aria-pressed="isFontSize(option.value)"
            @click="setFontSize(option.value)"
            :title="option.description"
          >
            <span class="option-label">{{ option.label }}</span>
            <span class="option-description">{{ option.description }}</span>
          </button>
        </div>
      </div>

      <!-- Alto Contraste -->
      <div class="setting-group">
        <label class="setting-label">
          <span class="label-text">Alto Contraste</span>
          <span class="label-description">Aumenta o contraste entre texto e fundo</span>
        </label>
        
        <button
          :class="[
            'toggle-button',
            { 'active': highContrast }
          ]"
          :aria-pressed="highContrast"
          @click="toggleHighContrast"
          :title="highContrast ? 'Desativar alto contraste' : 'Ativar alto contraste'"
        >
          <span class="toggle-icon">{{ highContrast ? '🔆' : '🌙' }}</span>
          <span class="toggle-text">
            {{ highContrast ? 'Ativado' : 'Desativado' }}
          </span>
        </button>
      </div>

      <!-- Redução de Movimento -->
       <!--
      <div class="setting-group">
        <label class="setting-label">
          <span class="label-text">Redução de Movimento</span>
          <span class="label-description">Reduz animações e transições</span>
        </label>
        
        <button
          :class="[
            'toggle-button',
            { 'active': reducedMotion }
          ]"
          :aria-pressed="reducedMotion"
          @click="toggleReducedMotion"
          :title="reducedMotion ? 'Desativar redução de movimento' : 'Ativar redução de movimento'"
        >
          <span class="toggle-icon">{{ reducedMotion ? '⏸️' : '▶️' }}</span>
          <span class="toggle-text">
            {{ reducedMotion ? 'Ativado' : 'Desativado' }}
          </span>
        </button>
      </div>
      -->

      <!-- Botão de Reset -->
      <div class="setting-group">
        <button
          class="reset-button"
          @click="resetSettings"
          title="Restaurar configurações padrão"
        >
          <span class="reset-icon">🔄</span>
          <span class="reset-text">Restaurar Padrões</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAccessibility } from '@/composables/useAccessibility';

const {
  fontSize,
  highContrast,
  reducedMotion,
  fontSizeOptions,
  setFontSize,
  toggleHighContrast,
  toggleReducedMotion,
  resetSettings,
  isFontSize,
} = useAccessibility();
</script>

<style scoped>
.accessibility-settings {
  padding: 1rem;
  background-color: var(--color-background-soft);
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.settings-header {
  margin-bottom: 1.5rem;
}

.settings-header h3 {
  margin: 0 0 0.5rem 0;
  color: var(--color-heading);
  font-size: var(--accessibility-font-size-large);
}

.settings-description {
  margin: 0;
  color: var(--color-text);
  font-size: var(--accessibility-font-size-small);
  opacity: 0.8;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.setting-label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.label-text {
  font-weight: 600;
  font-size: var(--accessibility-font-size);
}

.label-description {
  font-size: var(--accessibility-font-size-small);
  color: var(--color-text);
  opacity: 0.8;
}

/* Font Size Options */
.font-size-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
}

.font-size-option {
  padding: 0.75rem;
  border: 2px solid var(--color-border);
  border-radius: 6px;
  background-color: var(--color-background);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  color: var(--color-heading);
}

.font-size-option:hover {
  border-color: var(--color-border-hover);
  background-color: var(--color-background-soft);
}

.font-size-option.active {
  border-color: #007bff;
  background-color: #007bff;
  color: white;
}

.option-label {
  font-weight: 600;
  font-size: var(--accessibility-font-size);
}

.option-description {
  font-size: var(--accessibility-font-size-small);
  opacity: 0.8;
}

/* Toggle Buttons */
.toggle-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 2px solid var(--color-border);
  border-radius: 6px;
  background-color: var(--color-background);
  cursor: pointer;
  transition: all 0.2s ease;
  max-width: 200px;
  color: var(--color-heading);
}

.toggle-button:hover {
  border-color: var(--color-border-hover);
  background-color: var(--color-background-soft);
}

.toggle-button.active {
  border-color: #007bff;
  background-color: #007bff;
  color: white;
}

.toggle-icon {
  font-size: var(--accessibility-font-size-large);
}

.toggle-text {
  font-weight: 500;
  font-size: var(--accessibility-font-size);
}

/* Reset Button */
.reset-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 2px solid #dc3545;
  border-radius: 6px;
  background-color: transparent;
  color: #dc3545;
  cursor: pointer;
  transition: all 0.2s ease;
  max-width: 200px;
}

.reset-button:hover {
  background-color: #dc3545;
  color: white;
}

.reset-icon {
  font-size: var(--accessibility-font-size-large);
}

.reset-text {
  font-weight: 500;
  font-size: var(--accessibility-font-size);
}

/* High Contrast Mode Adjustments */
.high-contrast .accessibility-settings {
  border-color: #000000;
}

.high-contrast .font-size-option {
  border-color: #000000;
  background-color: #ffffff;
  color: #000000;
}

.high-contrast .font-size-option:hover {
  background-color: #f0f0f0;
}

.high-contrast .font-size-option.active {
  background-color: #000000;
  color: #ffffff;
}

.high-contrast .toggle-button {
  border-color: #000000;
  background-color: #ffffff;
  color: #000000;
}

.high-contrast .toggle-button:hover {
  background-color: #f0f0f0;
}

.high-contrast .toggle-button.active {
  background-color: #000000;
  color: #ffffff;
}

.high-contrast .reset-button {
  border-color: #000000;
  color: #000000;
}

.high-contrast .reset-button:hover {
  background-color: #000000;
  color: #ffffff;
}

/* Responsive Design */
@media (max-width: 768px) {
  .font-size-options {
    grid-template-columns: 1fr;
  }
  
  .toggle-button,
  .reset-button {
    max-width: none;
    width: 100%;
  }
}
</style>
