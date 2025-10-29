<!-- UsersList.vue - Refatorado com novo sistema UX -->
<template>
  <PageContainer
    title="Gerenciar Usuários"
    :global-loading="loading"
    :error="error || undefined"
    :empty="empty"
    empty-title="Nenhum usuário encontrado"
    empty-message="Não há usuários cadastrados no sistema."
    @retry="loadUsers"
  >
    <template #actions>
      <LoadingButton
        variant="primary"
        @click="openCreateModal"
      >
        Adicionar Usuário
      </LoadingButton>
    </template>

    <div class="users-content">
      <BaseTable 
        v-if="!loading && users.length > 0"
        :columns="columns" 
        :rows="users" 
        :sortKey="pagination.sortKey.value"
        :sortOrder="pagination.sortOrder.value" 
        keyField="id"
        @update:sort="handleSort"
      >
        <!-- Slot para coluna isMaster -->
        <template #cell-isMaster="{ value }">
          <span :class="['status-badge', value ? 'status-badge--success' : 'status-badge--secondary']">
            {{ value ? 'Sim' : 'Não' }}
          </span>
        </template>

        <!-- Slot para coluna isActive -->
        <template #cell-isActive="{ value }">
          <span :class="['status-badge', value ? 'status-badge--success' : 'status-badge--danger']">
            {{ value ? 'Ativo' : 'Inativo' }}
          </span>
        </template>

        <!-- Slot para coluna permissions -->
        <template #cell-permissionsList="{ row }">
          <LoadingButton
            variant="secondary"
            size="small"
            @click="openPermissionsModal(row)"
          >
            Editar permissões
          </LoadingButton>
        </template>

        <!-- Slot para coluna de ação edit -->
        <template #cell-edit="{ row }">
          <LoadingButton
            variant="secondary"
            size="small"
            @click="openEditModal(row)"
          >
            Editar
          </LoadingButton>
        </template>

        <!-- Slot para coluna de ação delete -->
        <template #cell-delete="{ row }">
          <LoadingButton
            variant="danger"
            size="small"
            @click="onDelete(row)"
          >
            Excluir
          </LoadingButton>
        </template>
      </BaseTable>
      
      <PaginationControls
        v-if="!loading && users.length > 0"
        :current-page="pagination.currentPage.value"
        :total-pages="pagination.totalPages.value"
        :total-items="pagination.totalItems.value"
        :page-size="pagination.pageSize.value"
        @go-to-page="pagination.goToPage"
        @change-page-size="pagination.updatePageSize"
      />
    </div>

    <!-- Modais -->
    <PermissionsModal 
      v-if="selectedUser" 
      :user="selectedUser" 
      :screens="allScreens"
      :initialPermissions="selectedUser.permissionsList" 
      @close="selectedUser = null" 
      @save="onSavePermissions" 
    />

    <UserEditModal
      v-if="selectedUserForEdit"
      :user="selectedUserForEdit"
      @cancel="selectedUserForEdit = null"
      @save="onSaveUser"
    />
      
    <UserCreateModal
      v-if="showCreateModal"
      @cancel="showCreateModal = false"
      @save="onCreateUser"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import BaseTable from '@/components/BaseTable.vue';
import PaginationControls from '@/components/PaginationControls.vue';
import PermissionsModal from '@/components/PermissionsModal.vue';
import UserEditModal from '@/components/UserEditModal.vue';
import UserCreateModal from '@/components/UserCreateModal.vue';
import PageContainer from '@/components/PageContainer.vue';
import LoadingButton from '@/components/LoadingButton.vue';
import { usePagination } from '@/composables/usePagination';
import { usePageState } from '@/composables/usePageState';
import { useErrorHandler } from '@/composables/useApiError';
import type { ColumnDef } from '@/composables/useTable';
import userService, { type User, type CreateUserData, type UpdateUserData } from '@/services/userService';

// Composables
const { handleError, handleSuccess, handleWarning } = useErrorHandler();
const { loading, error, data: users, empty, execute } = usePageState([]);

// Configurar paginação
const pagination = usePagination({
  pageSize: 10,
  initialPage: 1,
  initialSort: { key: 'username', order: 'asc' }
});

const allScreens = [
  { id: 'home', label: 'Home' },
  { id: 'estoques', label: 'Estoques' },
  { id: 'registrar_transacao', label: 'Registrar transação' },
  { id: 'consultar_transacoes', label: 'Consultar transações' },
  { id: 'custos_estoque', label: 'Custos do Estoque' },
  { id: 'cadastro_itens', label: 'Cadastro de Itens' },
  { id: 'suppliers', label: 'Cadastro de Fornecedores' },
  { id: 'cadastro_usuarios', label: 'Cadastro de Usuários' }
];

// Definição de colunas, agora incluindo a coluna 'delete'
const columns: ColumnDef<User>[] = [
    { key: 'username', label: 'Nome de usuário', sortable: true },
    { key: 'email', label: 'E-mail', sortable: true },
    { key: 'firstName', label: 'Nome', sortable: true },
    { key: 'lastName', label: 'Sobrenome', sortable: true },
    { key: 'isMaster', label: 'É usuário master?', sortable: true },
    { key: 'isActive', label: 'Está ativo?', sortable: true },
    { key: 'permissionsList' as keyof User, label: 'Permissões', sortable: false },
    { key: 'edit' as keyof User, label: 'Editar usuário', sortable: false },
    { key: 'delete' as keyof User, label: 'Deletar usuário', sortable: false }
];

// Função para buscar usuários
async function loadUsers() {
    await execute(async () => {
        const queryParams = pagination.getQueryParams();
        const result = await userService.getUsers(
            parseInt(queryParams.page), 
            {
                ordering: queryParams.ordering
            }
        );
        pagination.updateTotalItems(result.count);
        return result.results;
    });
}

// Carregar usuários ao montar o componente
onMounted(() => {
    loadUsers();
});

// Watchers para mudanças de paginação e ordenação
watch([
    () => pagination.currentPage.value,
    () => pagination.sortKey.value,
    () => pagination.sortOrder.value,
    () => pagination.pageSize.value
], () => {
    loadUsers();
});

// Função para ordenar
function handleSort(key: string) {
    pagination.setSort(key);
}

// Gerenciamento de permissões
const selectedUser = ref<User|null>(null);
function openPermissionsModal(user: User) {
  // Verifica se o usuário é master
  if (user.isMaster) {
    handleWarning('Usuário Master', 'Usuários master já possuem acesso total ao sistema. Não é necessário gerenciar suas permissões.');
    return;
  }
  
  selectedUser.value = user;
}

async function onSavePermissions(newPermissions: string[]) {
  if (!selectedUser.value) return;
  
  try {
    const updatedUser = await userService.updatePermissions(
      selectedUser.value.id, 
      newPermissions
    );
    
    // Atualiza o usuário na lista
    const idx = users.value.findIndex((u: User) => u.id === updatedUser.id);
    if (idx !== -1) users.value[idx] = updatedUser;
    
    selectedUser.value = null;
    handleSuccess('Permissões atualizadas', 'Permissões do usuário foram atualizadas com sucesso!');
  } catch (error) {
    handleError(error, 'Erro ao atualizar permissões');
  }
}

// Gerenciamento de edição de usuário
const selectedUserForEdit = ref<User|null>(null);
function openEditModal(user: User) {
    selectedUserForEdit.value = user;
}

// Ao salvar as alterações do usuário:
async function onSaveUser(updated: UpdateUserData) {
    if (!selectedUserForEdit.value) return;
    
    try {
        const updatedUser = await userService.updateUser(
            selectedUserForEdit.value.id,
            updated
        );
        
        // Atualiza no array original
        const idx = users.value.findIndex((u: User) => u.id === updatedUser.id);
        if (idx !== -1) users.value[idx] = updatedUser;
        
        selectedUserForEdit.value = null;
        handleSuccess('Usuário atualizado', 'Usuário foi atualizado com sucesso!');
    } catch (error) {
        handleError(error, 'Erro ao atualizar usuário');
    }
}

// Gerenciamento de criação de usuário
const showCreateModal = ref(false);
function openCreateModal() {
    showCreateModal.value = true;
}

async function onCreateUser(userData: CreateUserData) {
    try {
        const newUser = await userService.createUser(userData);
        // Recarregar a lista para mostrar o novo usuário
        await loadUsers();
        showCreateModal.value = false;
        handleSuccess('Usuário criado', 'Usuário foi criado com sucesso!');
    } catch (error) {
        handleError(error, 'Erro ao criar usuário');
    }
}

// Função para deletar usuário
async function onDelete(user: User) {
    if (confirm(`Tem certeza que deseja deletar o usuário "${user.username}"?`)) {
        try {
            await userService.deleteUser(user.id);
            // Recarregar a lista para atualizar a paginação
            await loadUsers();
            handleSuccess('Usuário excluído', 'Usuário foi excluído com sucesso!');
        } catch (error) {
            handleError(error, 'Erro ao excluir usuário');
        }
    }
}
</script>

<style scoped>
.users-content {
  /* background: white; */
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.status-badge--success {
  background: #dcfce7;
  color: #166534;
}

.status-badge--danger {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge--secondary {
  background: #f3f4f6;
  color: #374151;
}
</style>
