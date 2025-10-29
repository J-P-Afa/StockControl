<template>
    <div class="side-menu" :class="{ 'expanded': isExpanded }">
        <button @click="toggleExpansion" class="menu-button">
            <span>{{ isExpanded ? '◀' : '☰' }}</span>
        </button>
        <div class="menu-content">
            <ul>
                <!-- Home sempre visível -->
                <MenuItem class="menu-item" to="/" label="Home" v-if="hasPermission('home')" />
                <MenuItem class="menu-item" to="/estoques" label="Estoques" v-if="hasPermission('estoques')" />
                <MenuItem class="menu-item" to="/registrar-transacao" label="Registrar transação" v-if="hasPermission('registrar_transacao')" />
                <MenuItem class="menu-item" to="/consultar-transacoes" label="Consultar transações" v-if="hasPermission('consultar_transacoes')" />
                <MenuItem class="menu-item" to="/custos" label="Custos do Estoque" v-if="hasPermission('custos_estoque')" />
                <MenuItem class="menu-item" to="/itens" label="Cadastro de Itens" v-if="hasPermission('cadastro_itens')" />
                <MenuItem class="menu-item" to="/fornecedores" label="Cadastro de Fornecedores" v-if="hasPermission('suppliers')" />
                <MenuItem class="menu-item" to="/usuarios" label="Cadastro de Usuários" v-if="hasPermission('cadastro_usuarios')" />
                <MenuItem class="menu-item" to="/logout" label="Logout" @click="handleLogout" />
            </ul>
            
            <!-- Botão de Acessibilidade -->
            <div class="accessibility-section">
                <button @click="toggleAccessibilityModal" class="accessibility-button" title="Configurações de Acessibilidade">
                    <span class="accessibility-icon">♿</span>
                    <span class="accessibility-label" v-if="isExpanded">Acessibilidade</span>
                </button>
            </div>
        </div>
        
        <!-- Modal de Acessibilidade -->
        <div v-if="showAccessibilityModal" class="modal-backdrop" @click="closeAccessibilityModal">
            <div class="modal accessibility-modal" @click.stop>
                <div class="modal-header">
                    <h2>Configurações de Acessibilidade</h2>
                    <button @click="closeAccessibilityModal" class="close-button" title="Fechar">
                        <span>✖</span>
                    </button>
                </div>
                <div class="modal-content">
                    <AccessibilitySettings />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, defineComponent, h, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSideMenu } from '@/composables/useSideMenu'
import AccessibilitySettings from './AccessibilitySettings.vue'

const authStore = useAuthStore()
const { isExpanded, toggleExpansion } = useSideMenu()
const showAccessibilityModal = ref(false)

const toggleAccessibilityModal = () => {
    showAccessibilityModal.value = !showAccessibilityModal.value
}

const closeAccessibilityModal = () => {
    showAccessibilityModal.value = false
}

const handleLogout = () => {
    if (confirm('Tem certeza que deseja sair?')) {
        authStore.logout()
    }
}

// Verifica se o usuário tem permissão para acessar determinada rota
const hasPermission = (permission: string): boolean => {
    // Se não há usuário atual, não mostra nada
    if (!authStore.currentUser) return false;
    
    // Usuários master têm acesso a tudo
    if (authStore.currentUser.isMaster) return true;
    
    // Verifica se o usuário tem a permissão específica
    return authStore.currentUser.permissionsList.includes(permission);
}

interface MenuItemProps {
    to: string;
    label: string;
    onClick?: () => void;
    class?: string;
}

const MenuItem = defineComponent({
    props: {
        to: { type: String, required: true },
        label: { type: String, required: true },
        onClick: { type: Function, required: false },
        class: { type: String, required: false }
    },
    setup(props: MenuItemProps) {
        return () =>
            h('li', [
                h(RouterLink, 
                    { 
                        to: props.to, 
                        class: props.class,
                        onClick: props.onClick
                    }, 
                    props.label
                )
            ]);
    }
});
</script>

<style scoped>

.menu-item {
    padding: 5px 10px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.side-menu {
    position: fixed;
    top: 0;
    left: 0;
    width: 60px;
    height: 100vh;
    background-color: #333;
    color: white;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    z-index: 1000;
    overflow-y: auto;
    transition: width 0.3s ease;
}

.side-menu.expanded {
    width: 250px;
}

.menu-button {
    background-color: #444;
    border: none;
    padding: 10px;
    cursor: grab;
    font-size: 20px;
}

.menu-item {
    padding: 5px 10px;
    cursor: pointer;
    transition: background-color 0.3s;
}



.menu-button:hover {
    background-color: #555;
}

.menu-content {
    margin-top: 20px;
    width: 100%;
    padding: 0 10px;
    overflow: hidden;
}

.side-menu:not(.expanded) .menu-content {
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease, visibility 0.3s ease;
}

.side-menu.expanded .menu-content {
    opacity: 1;
    visibility: visible;
    transition: opacity 0.3s ease, visibility 0.3s ease;
}

.menu-content ul {
    list-style-type: none;
    padding: 0;
    margin: 0;
}

.menu-content li {
    margin: 10px 0;
}

.menu-content a {
    color: white;
    text-decoration: none;
    display: flex;
    align-items: center;
    padding: 8px 12px;
    border-radius: 4px;
    transition: background-color 0.3s;
}

.menu-content a:hover {
    background-color: #555;
    text-decoration: none;
}

.menu-content a.active {
    font-weight: bold;
    color: #ff0;
    background-color: #555;
    text-decoration: none;
}

/* Accessibility Section */
.accessibility-section {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #555;
}

.side-menu:not(.expanded) .accessibility-section {
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease, visibility 0.3s ease;
}

.side-menu.expanded .accessibility-section {
    opacity: 1;
    visibility: visible;
    transition: opacity 0.3s ease, visibility 0.3s ease;
}

.accessibility-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 15px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.3s;
    width: 100%;
    font-size: 14px;
}

.side-menu:not(.expanded) .accessibility-button {
    padding: 10px;
    justify-content: center;
}

.accessibility-button:hover {
    background-color: #0056b3;
}

.accessibility-icon {
    font-size: 16px;
}

.accessibility-label {
    font-weight: 500;
}

/* Accessibility Modal */
.accessibility-modal {
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
    margin: 0;
    color: var(--color-heading);
    font-size: var(--accessibility-font-size-large);
}

.close-button {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    padding: 5px;
    border-radius: 4px;
    transition: background-color 0.2s;
    color: var(--color-text);
}

.close-button:hover {
    background-color: var(--color-background-soft);
}

.modal-content {
    padding: 0;
}

/* High Contrast Mode for Modal */
.high-contrast .accessibility-button {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: 2px solid #000000 !important;
}

.high-contrast .accessibility-button:hover {
    background-color: #333333 !important;
}

.high-contrast .modal-header {
    border-bottom-color: #000000 !important;
}

.high-contrast .close-button {
    color: #000000 !important;
    border: 1px solid #000000 !important;
}

.high-contrast .close-button:hover {
    background-color: #f0f0f0 !important;
}

/* Responsividade */
@media (max-width: 768px) {
    .side-menu {
        width: 50px;
    }
    
    .side-menu.expanded {
        width: 200px;
    }
    
    .menu-button {
        padding: 8px;
        font-size: 16px;
    }
    
    .menu-content {
        margin-top: 10px;
        padding: 0 5px;
    }
    
    .menu-content li {
        margin: 5px 0;
    }
    
    .menu-content a {
        padding: 6px 8px;
        font-size: 14px;
    }
    
    .accessibility-section {
        margin-top: 10px;
        padding-top: 10px;
    }
    
    .accessibility-button {
        padding: 8px 10px;
        font-size: 12px;
    }
}

</style>
