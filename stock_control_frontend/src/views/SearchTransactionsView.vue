<template>
  <PageContainer
    title="Consultar Transações"
    :global-loading="loading"
    :error="error"
    @retry="loadTransactions"
  >
    <!--<template #actions>
      <LoadingButton
        variant="primary"
        @click="openNewTransactionModal"
      >
        Nova Transação
      </LoadingButton>
    </template>-->

    <div class="transactions-content">
      <!-- Filtros -->
      <div class="filters-section">
        <h3>Filtros de Busca</h3>
        <TransactionsFilters v-model="filters" @search="onSearch" />
      </div>
      
      <!-- Lista de Transações -->
      <div class="transactions-section">
        <h3>Lista de Transações</h3>
        <TransactionsList 
          :filters="filters" 
          :refreshKey="refreshKey" 
          @edit="onEditTransaction" 
          @delete="onDeleteTransaction" 
        />
      </div>
    </div>

    <!-- Modal de Edição -->
    <!--
    <div v-if="showEditTransactionModal" class="modal-backdrop" @click="closeEditModal">
      <div class="modal form-container" @click.stop>
        <div class="modal-header">
          <h2>Editar Transação</h2>
          <button class="modal-close" @click="closeEditModal" aria-label="Fechar">
            <svg viewBox="0 0 24 24" fill="currentColor" class="close-icon">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
        <TransactionForm 
          :isEditMode="true" 
          :transaction="transactionToEdit || undefined" 
          @submit="onEditTransactionSave" 
          @cancel="closeEditModal" 
        />
      </div>
    </div>
    -->

    
    <!-- Modal de Nova Transação -->
    <!--
    <div v-if="showNewTransactionModal" class="modal-backdrop" @click="closeNewModal">
      <div class="modal form-container" @click.stop>
        <div class="modal-header">
          <h2>Nova Transação</h2>
          <button class="modal-close" @click="closeNewModal" aria-label="Fechar">
            <svg viewBox="0 0 24 24" fill="currentColor" class="close-icon">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
        <TransactionForm 
          @submit="onNewTransactionSave" 
          @cancel="closeNewModal" 
        />
      </div>
    </div>
    -->
  </PageContainer>
</template>
  
<script setup lang="ts">
import { ref, watch } from 'vue';
import TransactionsFilters from '@/components/TransactionsFilters.vue';
import TransactionsList from '@/components/TransactionsList.vue';
import TransactionFormImproved from '@/components/TransactionFormImproved.vue';
import PageContainer from '@/components/PageContainer.vue';
import LoadingButton from '@/components/LoadingButton.vue';
import { usePageState } from '@/composables/usePageState';
import { useErrorHandler } from '@/composables/useApiError';
import { getCurrentBrazilianDate } from '@/utils/date';
import { transactionService, type FormattedTransaction } from '@/services/transactionService';
  
// Composables
const { handleError, handleSuccess, handleWarning } = useErrorHandler();
const { loading, error, execute } = usePageState();

// Estado para filtros
interface TransactionFilters {
  transactionsDateFrom: string;
  transactionsDateTo: string;
  itemSKU: string;
  itemDescription: string;
  notaFiscal: string;
  showInUSD: boolean;
}

// Inicializar com a data de hoje
const today = getCurrentBrazilianDate();

// Estado dos filtros
const filters = ref<TransactionFilters>({
  transactionsDateFrom: today,
  transactionsDateTo: today,
  itemSKU: '',
  itemDescription: '',
  notaFiscal: '',
  showInUSD: false
});

// Chave reativa para forçar reload
const refreshKey = ref(0);

// Controle dos modais
const showNewTransactionModal = ref(false);
const showEditTransactionModal = ref(false);
const transactionToEdit = ref<FormattedTransaction | null>(null);
  
// Métodos
const loadTransactions = async () => {
  await execute(async () => {
    // Simula carregamento de dados da página
    await new Promise(resolve => setTimeout(resolve, 500));
    return { message: 'Transações carregadas' };
  });
};

// Quando o usuário clica em buscar
function onSearch() {
  console.log('TransactionsView: onSearch called');
  console.log('TransactionsView: Filtros atuais:', filters.value);
  
  // Incrementa para disparar watcher em TransactionsList
  refreshKey.value++;
  console.log('TransactionsView: refreshKey incrementado para:', refreshKey.value);
}

// Abrir modal de nova transação
function openNewTransactionModal() {
  showNewTransactionModal.value = true;
}

// Fechar modais
function closeNewModal() {
  showNewTransactionModal.value = false;
}

function closeEditModal() {
  showEditTransactionModal.value = false;
  transactionToEdit.value = null;
}

// Salvar nova transação
async function onNewTransactionSave(transaction: any) {
  try {
    // A implementação real de salvar está no TransactionForm
    showNewTransactionModal.value = false;
    onSearch();
    handleSuccess('Transação criada', 'Transação foi criada com sucesso!');
  } catch (err) {
    handleError(err, 'Erro ao cadastrar transação');
  }
}

// Editar transação
function onEditTransaction(transaction: any) {
  transactionToEdit.value = { ...transaction };
  showEditTransactionModal.value = true;
}

// Salvar edição de transação
async function onEditTransactionSave(transaction: any) {
  transaction.id = transactionToEdit.value?.id;
  transaction.idTransacao = transactionToEdit.value?.cronology;
  
  try {
    await transactionService.updateTransaction(transaction as FormattedTransaction);
    showEditTransactionModal.value = false;
    onSearch();
    transactionToEdit.value = null;
    handleSuccess('Transação atualizada', 'Transação foi atualizada com sucesso!');
  } catch (err) {
    handleError(err, 'Erro ao editar transação');
    showEditTransactionModal.value = false;
  }
}

// Deletar transação
async function onDeleteTransaction(transaction: any) {
  if (confirm(`Tem certeza que deseja deletar esta transação?`)) {
    try {
      await transactionService.deleteTransaction(transaction.id);
      onSearch();
      handleSuccess('Transação excluída', 'Transação foi excluída com sucesso!');
    } catch (err) {
      handleError(err, 'Erro ao excluir transação');
    }
  }
}
</script>

<style scoped>
.transactions-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filters-section,
.transactions-section {
  /*background: white;*/
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.filters-section h3,
.transactions-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  /*color: #1f2937;*/
}

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
  max-width: 800px;
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
  /*color: #6b7280;*/
  transition: all 0.2s ease;
}

.modal-close:hover {
  /*background: #f3f4f6;*/
  /*color: #374151;*/
}

.close-icon {
  width: 20px;
  height: 20px;
}

@media (max-width: 768px) {
  .transactions-content {
    gap: 16px;
  }
  
  .filters-section,
  .transactions-section {
    padding: 16px;
  }
  
  .modal-backdrop {
    padding: 10px;
  }
  
  .modal-header {
    padding: 16px 16px 0 16px;
  }
}
</style>