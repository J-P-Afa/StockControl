<template>
  <PageContainer
    title="Sobre o Sistema"
    :global-loading="loading"
    :error="error"
    @retry="loadAboutData"
  >
    <div class="about-content">
      <div class="about-card">
        <div class="about-header">
          <h2>Sistema de Controle de Estoque</h2>
          <p class="about-subtitle">Gerencie seu estoque de forma eficiente e organizada</p>
        </div>

        <div class="about-features">
          <h3>Funcionalidades Principais</h3>
          <div class="features-grid">
            <div class="feature-item">
              <div class="feature-icon">📦</div>
              <h4>Gestão de Itens</h4>
              <p>Cadastre e gerencie produtos com SKU, descrição e unidade de medida</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">🏭</div>
              <h4>Fornecedores</h4>
              <p>Controle de fornecedores e suas informações de contato</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <h4>Transações</h4>
              <p>Registre entradas e saídas de estoque com controle de custos</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">💰</div>
              <h4>Custos</h4>
              <p>Acompanhe custos médios e últimos custos de entrada</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">👥</div>
              <h4>Usuários</h4>
              <p>Sistema de permissões e controle de acesso</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">📈</div>
              <h4>Relatórios</h4>
              <p>Visualize relatórios de estoque e movimentações</p>
            </div>
          </div>
        </div>

        <div class="about-info">
          <h3>Informações do Sistema</h3>
          <div class="info-grid">
            <div class="info-item">
              <strong>Versão:</strong> 1.0.0
            </div>
            <div class="info-item">
              <strong>Desenvolvido com:</strong> Vue.js 3 + TypeScript
            </div>
            <div class="info-item">
              <strong>Backend:</strong> Django REST Framework
            </div>
            <div class="info-item">
              <strong>Banco de Dados:</strong> SQLite
            </div>
          </div>
        </div>
      </div>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import PageContainer from '@/components/PageContainer.vue';
import { usePageState } from '@/composables/usePageState';
import { useErrorHandler } from '@/composables/useApiError';

// Composables
const { handleError } = useErrorHandler();
const { loading, error, execute } = usePageState();

// Métodos
const loadAboutData = async () => {
  await execute(async () => {
    // Simula carregamento de dados da página
    await new Promise(resolve => setTimeout(resolve, 500));
    return { message: 'Informações carregadas' };
  });
};
</script>

<style scoped>
.about-content {
  max-width: 1000px;
  margin: 0 auto;
}

.about-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 32px;
}

.about-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 24px;
  border-bottom: 2px solid #e5e7eb;
}

.about-header h2 {
  margin: 0 0 12px 0;
  font-size: 28px;
  font-weight: 700;
  /*color: #1f2937;*/
}

.about-subtitle {
  margin: 0;
  font-size: 16px;
  color: #6b7280;
}

.about-features {
  margin-bottom: 40px;
}

.about-features h3 {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
  /*color: #1f2937;*/
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.feature-item {
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  text-align: center;
  transition: all 0.2s ease;
}

.feature-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.feature-item h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  /*color: #1f2937;*/
}

.feature-item p {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
}

.about-info {
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.about-info h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  /*color: #1f2937;*/
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.info-item {
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 6px;
  font-size: 14px;
  color: #374151;
}

.info-item strong {
  /*color: #1f2937;*/
}

@media (max-width: 768px) {
  .about-card {
    padding: 24px;
  }
  
  .about-header h2 {
    font-size: 24px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
