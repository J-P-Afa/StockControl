<script setup lang="ts">
import { onMounted } from 'vue';
import HomePageSuggestions from '../components/HomePageSuggestions.vue';
import PageContainer from '../components/PageContainer.vue';
import { usePageState } from '../composables/usePageState';
import { useErrorHandler } from '../composables/useApiError';

const { handleSuccess } = useErrorHandler();
const { loading, error, execute } = usePageState();

// Simula carregamento de dados da página inicial
const loadHomeData = async () => {
  await execute(async () => {
    // Aqui você pode carregar dados específicos da página inicial
    // Por exemplo: estatísticas, notificações, etc.
    await new Promise(resolve => setTimeout(resolve, 1000)); // Simula delay
    return { message: 'Página inicial carregada' };
  });
};

onMounted(() => {
  loadHomeData();
});
</script>

<template>
  <PageContainer
    title="Dashboard"
    :global-loading="loading"
    loading-message="Carregando dashboard..."
    :error="error"
    @retry="loadHomeData"
  >
  <!--
    <template #actions>
      <button class="btn btn-primary" @click="handleSuccess('Ação executada', 'Operação realizada com sucesso!')">
        Testar Notificação
      </button>
    </template>
    -->
    <main>
      <HomePageSuggestions />
    </main>
  </PageContainer>
</template>
