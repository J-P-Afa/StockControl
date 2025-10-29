<template>
  <PageContainer
    title="Inserir Transação"
    :global-loading="loading"
    :error="error"
    @retry="loadTransactionForm"
  >
    <div class="transaction-form-container">
      <TransactionFormImproved @submit="onTransactionSubmit" @cancel="onTransactionCancel" />
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import TransactionFormImproved from '@/components/TransactionFormImproved.vue';
import PageContainer from '@/components/PageContainer.vue';
import { usePageState } from '@/composables/usePageState';
import { useErrorHandler } from '@/composables/useApiError';

// Composables
const router = useRouter();
const { handleError, handleSuccess } = useErrorHandler();
const { loading, error, execute } = usePageState();

// Métodos
const loadTransactionForm = async () => {
  await execute(async () => {
    // Simula carregamento de dados da página
    await new Promise(resolve => setTimeout(resolve, 500));
    return { message: 'Formulário carregado' };
  });
};

const onTransactionSubmit = (transaction: any) => {
  // Redireciona para a lista de transações
  router.push('/transactions');
};

const onTransactionCancel = () => {
  // Redireciona para a lista de transações
  router.push('/transactions');
};
</script>

<style scoped>
.transaction-form-container {
  /*background: white;*/
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

@media (max-width: 768px) {
  .transaction-form-container {
    padding: 16px;
  }
}
</style>
