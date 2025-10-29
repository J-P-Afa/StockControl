<!-- LoginView.vue -->
<template>
    <div class="login-container">
        <form @submit.prevent.stop class="login-form">
            <h1>Login</h1>
            
            <!-- Mensagem de erro -->
            <div v-if="errorMessage" class="error-message">
                {{ errorMessage }}
            </div>
            
            <div class="form-group">
                <label for="username">Usuário</label>
                <input
                    type="text"
                    id="username"
                    v-model="username"
                    required
                    autocomplete="username"
                    :class="{ 'input-error': errorMessage }"
                    @input="clearError"
                />
            </div>
            <div class="form-group">
                <label for="password">Senha</label>
                <input
                    type="password"
                    id="password"
                    v-model="password"
                    required
                    autocomplete="current-password"
                    :class="{ 'input-error': errorMessage }"
                    @input="clearError"
                />
            </div>
            <LoadingButton 
                type="button"
                :loading="loading"
                variant="primary"
                size="large"
                class="login-button"
                @click="onSubmit"
            >
                Entrar
            </LoadingButton>
        </form>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useErrorHandler } from '@/composables/useApiError'
import LoadingButton from '@/components/LoadingButton.vue'

const router = useRouter()
const authStore = useAuthStore()
const { handleError, handleSuccess } = useErrorHandler()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

function clearError() {
    errorMessage.value = ''
}

async function onSubmit() {
    try {
        console.log('LoginView: Iniciando login')
        loading.value = true
        errorMessage.value = ''
        
        await authStore.login({ username: username.value, password: password.value })
        console.log('LoginView: Login bem sucedido')
        
        handleSuccess('Login realizado', 'Bem-vindo de volta!')
        
        // Redireciona para a página inicial
        router.push('/')
    } catch (err: any) {
        console.error('LoginView: Erro no login:', err)
        
        // Define mensagem de erro amigável
        if (err.response && err.response.status === 401) {
            errorMessage.value = 'Usuário ou senha inválidos. Por favor, tente novamente.'
        } else if (err.message && err.message.includes('Network Error')) {
            errorMessage.value = 'Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.'
        } else {
            errorMessage.value = 'Ocorreu um erro ao tentar fazer login. Por favor, tente novamente.'
        }
        
        // Limpa o campo de senha
        password.value = ''
        
        // Mantém o foco no campo de senha
        document.getElementById('password')?.focus()
    } finally {
        loading.value = false
    }
}
</script>

<style lang="css">
html,
body {
    margin: 0;
    padding: 0;
    overflow-x: hidden;
    height: 100%;
}

.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.login-form {
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
}

.form-group {
    margin-bottom: 1rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
}

input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

button {
    width: 100%;
    padding: 0.75rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
}

button:disabled {
    background-color: grey;
    cursor: not-allowed;
}

.error-message {
    background-color: #fee2e2;
    color: #dc2626;
    padding: 0.75rem 1rem;
    border-radius: 0.375rem;
    margin-bottom: 1.25rem;
    border-left: 4px solid #dc2626;
    font-size: 0.875rem;
}

.input-error {
    border-color: #f87171 !important;
    box-shadow: 0 0 0 1px #f87171;
}

.login-button {
    margin-top: 0.5rem;
}

/* Animações */
.error-message {
    animation: shake 0.5s ease-in-out;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}
</style>