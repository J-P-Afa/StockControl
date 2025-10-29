<template>
    <div class="homepage-title">
        <h1 class="homepage-title-text">Controle de estoque projeto congonhas</h1>
        <p class="welcome-message" v-if="authStore.currentUser">
            Bem-vindo(a), <strong>{{ authStore.currentUser.username }}</strong>!
            <span v-if="authStore.currentUser.isMaster" class="master-badge">Usuário Master</span>
        </p>
    </div>
    <div class="suggestion-items">
        <h2 class="suggestion-title">Acessos rápidos</h2>
        
        <!-- Mostra sugestões baseadas nas permissões do usuário -->
        <router-link 
            v-if="hasPermission('estoques')" 
            to="/estoques" 
            class="suggestion-item">
            <button class="suggestion-item-button">
                <span>Estoques</span>
            </button>
        </router-link>
        
        <router-link 
            v-if="hasPermission('custos_estoque')" 
            to="/custos" 
            class="suggestion-item">
            <button class="suggestion-item-button">
                <span>Custos do estoque</span>
            </button>
        </router-link>
        
        <router-link 
            v-if="hasPermission('registrar_transacao')" 
            to="/registrar-transacao" 
            class="suggestion-item">
            <button class="suggestion-item-button">
                <span>Registrar transação</span>
            </button>
        </router-link>
        
        <router-link 
            v-if="hasPermission('consultar_transacoes')" 
            to="/consultar-transacoes" 
            class="suggestion-item">
            <button class="suggestion-item-button">
                <span>Consultar transações</span>
            </button>
        </router-link>
        
        <router-link 
            v-if="hasPermission('cadastro_itens')" 
            to="/itens" 
            class="suggestion-item">
            <button class="suggestion-item-button">
                <span>Cadastro de itens</span>
            </button>
        </router-link>
        
        <div v-if="!hasSuggestions" class="no-suggestions">
            <p>Seu usuário tem acesso limitado. Entre em contato com um administrador para mais permissões.</p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';

const authStore = useAuthStore();

// Verifica se o usuário tem permissão para acessar determinada rota
const hasPermission = (permission: string): boolean => {
    // Se não há usuário atual, não mostra nada
    if (!authStore.currentUser) return false;
    
    // Usuários master têm acesso a tudo
    if (authStore.currentUser.isMaster) return true;
    
    // Verifica se o usuário tem a permissão específica
    return authStore.currentUser.permissionsList.includes(permission);
};

// Verifica se há pelo menos uma sugestão para mostrar
const hasSuggestions = computed(() => {
    return hasPermission('estoques') || 
           hasPermission('custos_estoque') || 
           hasPermission('registrar_transacao') || 
           hasPermission('consultar_transacoes') || 
           hasPermission('cadastro_itens');
});
</script>

<style scoped>
.homepage-title {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 2rem 0;
}

.welcome-message {
    margin-top: 1rem;
    font-size: 1.2rem;
    color: var(--color-gray-400);
}

.master-badge {
    display: inline-block;
    background-color: #007bff;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    font-weight: bold;
    margin-left: 0.5rem;
}

.suggestion-title {
    font-size: 1.75rem;
    font-weight: bold;
    margin-bottom: 1.5rem;
    text-align: center;
    color: var(--color-white);
}

.suggestion-items {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-width: 600px;
    margin: 0 auto;
}

.suggestion-item {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 50px;
    /*background-color: #f8f9fa;*/
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-decoration: none;
    transition: transform 0.2s, box-shadow 0.2s;
}

.suggestion-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.suggestion-item-button {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    background-color: var(--color-primary);
    border: none;
    cursor: pointer;
    color: var(--color-white);
}

.suggestion-item-button:hover {
    /*background-color: #e9ecef;*/
    border-radius: 8px;
}

.suggestion-item-button span {
    font-size: 1.25rem;
    font-weight: 500;
}

.no-suggestions {
    text-align: center;
    padding: 2rem;
    border-radius: 8px;
    color: var(--color-gray-400);
}
</style>
