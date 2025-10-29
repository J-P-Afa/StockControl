<!-- SuppliersView.vue - Refatorado com novo sistema UX -->
<template>
  <PageContainer
    title="Cadastro de Fornecedores"
    :global-loading="loading"
    :error="error"
    @retry="loadSuppliers"
  >
    <template #actions>
      <LoadingButton
        variant="primary"
        @click="showNewSupplierModal = true"
      >
        Cadastrar Fornecedor
      </LoadingButton>
    </template>

    <div class="suppliers-content">
      <!-- Filtros -->
      <div class="filters-section">
        <h3>Filtros de Busca</h3>
        <SuppliersFilters v-model="filters" @search="onSearch" />
      </div>

      <!-- Lista de Fornecedores -->
      <div class="suppliers-section">
        <h3>Lista de Fornecedores</h3>
        <SuppliersList 
          :filters="filters" 
          :refreshKey="refreshKey" 
          @edit="onEditSupplier" 
          @delete="onDeleteSupplier" 
        />
      </div>
    </div>

    <!-- Modal de Novo Fornecedor -->
    <div v-if="showNewSupplierModal" class="modal-backdrop" @click="closeNewModal">
      <div class="modal form-container" @click.stop>
        <div class="modal-header">
          <h2>Cadastrar Novo Fornecedor</h2>
          <button class="modal-close" @click="closeNewModal" aria-label="Fechar">
            <svg viewBox="0 0 24 24" fill="currentColor" class="close-icon">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
        <SupplierEditModal
          :supplier="emptySupplier"
          @cancel="closeNewModal"
          @save="onNewSupplierSave"
        />
      </div>
    </div>

    <!-- Modal de Edição -->
    <div v-if="showEditSupplierModal && supplierToEdit" class="modal-backdrop" @click="closeEditModal">
      <div class="modal form-container" @click.stop>
        <div class="modal-header">
          <h2>Editar Fornecedor</h2>
          <button class="modal-close" @click="closeEditModal" aria-label="Fechar">
            <svg viewBox="0 0 24 24" fill="currentColor" class="close-icon">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
        <SupplierEditModal
          :supplier="supplierToEdit"
          @cancel="closeEditModal"
          @save="onEditSupplierSave"
        />
      </div>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import SuppliersFilters from '@/components/SuppliersFilters.vue';
import SuppliersList from '@/components/SuppliersList.vue';
import SupplierEditModal from '@/components/SupplierEditModal.vue';
import PageContainer from '@/components/PageContainer.vue';
import LoadingButton from '@/components/LoadingButton.vue';
import { usePageState } from '@/composables/usePageState';
import { useErrorHandler } from '@/composables/useApiError';
import { supplierService, type Fornecedor } from '@/services/supplierService';

// Composables
const { handleError, handleSuccess } = useErrorHandler();
const { loading, error, execute } = usePageState();

interface SupplierFilters {
  supplierName: string;
  showOnlyActive: boolean;
}

const filters = ref<SupplierFilters>({
  supplierName: '',
  showOnlyActive: true,
});

// chave reativa para forçar reload
const refreshKey = ref(0);

// controle do modal
const showNewSupplierModal = ref(false);
const showEditSupplierModal = ref(false);
const supplierToEdit = ref<Fornecedor>({
  codFornecedor: 0,
  nomeFornecedor: '',
  active: true,
});
const emptySupplier: Fornecedor = {
  codFornecedor: 0,
  nomeFornecedor: '',
  active: true,
};

// Métodos
const loadSuppliers = async () => {
  await execute(async () => {
    // Simula carregamento de dados da página
    await new Promise(resolve => setTimeout(resolve, 500));
    return { message: 'Fornecedores carregados' };
  });
};

function onSearch() {
  console.log('SuppliersView: Evento de busca recebido');
  console.log('SuppliersView: Filtros atuais:', filters.value);
  
  // incrementa para disparar watcher em SuppliersList
  refreshKey.value++;
  console.log('SuppliersView: refreshKey incrementado para:', refreshKey.value);
}

// observa mudanças nos filtros
watch(filters, (newValue) => {
  console.log('SuppliersView: Filtros atualizados:', newValue);
  // Não precisamos chamar onSearch aqui, pois o SuppliersFilters já emite o evento search
}, { deep: true });

// Fechar modais
function closeNewModal() {
  showNewSupplierModal.value = false;
}

function closeEditModal() {
  showEditSupplierModal.value = false;
  supplierToEdit.value = {
    codFornecedor: 0,
    nomeFornecedor: '',
    active: true,
  };
}

async function onNewSupplierSave(newSupplier: Fornecedor) {
  try {
    await supplierService.createSupplier(newSupplier);
    showNewSupplierModal.value = false;
    onSearch();
    handleSuccess('Fornecedor criado', 'Fornecedor foi criado com sucesso!');
  } catch (err) {
    handleError(err, 'Erro ao cadastrar fornecedor');
  }
}

function onEditSupplier(supplier: Fornecedor) {
  supplierToEdit.value = { ...supplier };
  showEditSupplierModal.value = true;
}

async function onEditSupplierSave(updatedSupplier: Fornecedor) {
  try {
    await supplierService.updateSupplier(updatedSupplier);
    showEditSupplierModal.value = false;
    onSearch();
    handleSuccess('Fornecedor atualizado', 'Fornecedor foi atualizado com sucesso!');
  } catch (err) {
    handleError(err, 'Erro ao editar fornecedor');
  }
}

async function onDeleteSupplier(supplier: Fornecedor) {
  if (confirm(`Tem certeza que deseja deletar o fornecedor "${supplier.nomeFornecedor}"?`)) {
    try {
      await supplierService.deleteSupplier(supplier.codFornecedor);
      onSearch();
      handleSuccess('Fornecedor excluído', 'Fornecedor foi excluído com sucesso!');
    } catch (err) {
      handleError(err, 'Erro ao excluir fornecedor');
    }
  }
}
</script>

<style scoped>
.suppliers-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filters-section,
.suppliers-section {
  /* background: white; */
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.filters-section h3,
.suppliers-section h3 {
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

@media (max-width: 768px) {
  .suppliers-content {
    gap: 16px;
  }
  
  .filters-section,
  .suppliers-section {
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