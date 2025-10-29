<template>
    <div class="users-view view">
        <h1>Cadastro de usuários</h1>
        <div class="users-list list-container">
        <h2>Usuários</h2>
            <UsersList />
        </div>
    </div>
</template>
<script setup lang="ts">
import UsersList from '@/components/UsersList.vue';
</script>

<style scoped>
.users-view {
  width: 90%;
  margin-left: 6%;
}
</style>