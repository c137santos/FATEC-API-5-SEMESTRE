<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-4">
      <div class="text-h2 ma-2 pa-2">Users</div>

      <v-btn
        color="blue-darken-4"
        prepend-icon="mdi-account-plus"
        @click="formCadastro"
      >
        Cadastrar novo usuário
      </v-btn>
    </div>

    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      :headers="headers"
      :items="users"
      :items-length="totalUsers"
      :loading="loading"
      @update:options="loadUsers"
    >
      <template v-slot:item.actions="{ item }">
        <v-btn
          icon
          variant="text"
          color="black"
          @click="abrirEdit(item)"
        >
          <v-icon>mdi-pencil</v-icon>
        </v-btn>

        <v-btn
          icon
          variant="text"
          color="black"
          @click="abrirDelete(item)"
        >
          <v-icon>mdi-delete</v-icon>
        </v-btn>
      </template>

      <template v-slot:no-data>
        <div class="text-center pa-4">Nenhum usuário encontrado.</div>
      </template>
    </v-data-table-server>
  </v-container>
</template>


<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import accountsApi from "@/api/accounts.api";

const headers = ref([
  { title: "Id", key: "id", align: "start" },
  { title: "Nome", key: "name", align: "start" },
  { title: "E-mail", key: "email", align: "start" },
  { title: "Tipo de acesso", key: "permissions", align: "start" },
  { key: "actions", align: "center", sortable: false },
]);

const route = useRoute();
const users = ref([]);
const itemsPerPage = ref(10);
const totalUsers = ref(0);
const loading = ref(true);
const dialogAberto = ref(false);
const userSelecionado = ref(null);

const formCadastro = () => {
  route.push('/accounts/users/create');
};

const abrirEdit = (user) => {
  userSelecionado.value = user;
  dialogAberto.value = true;
};

const abrirDelete = (user) => {
  userSelecionado.value = user;
  dialogAberto.value = true;
};

const searchUsers = async (page = 1, limit = itemsPerPage.value, sortBy = []) => {
  loading.value = true;
  try {
    const response = await accountsApi.getUsers(page, limit, sortBy);
    users.value = response.users || [];
    totalUsers.value = response.total_items || 0;
  } catch (error) {
    console.error("Erro ao buscar usuários:", error);
    users.value = [];
    totalUsers.value = 0;
  } finally {
    loading.value = false;
  }
};

const loadUsers = async ({ page, itemsPerPage, sortBy }) => {
  await searchUsers(page, itemsPerPage, sortBy);
};

onMounted(async () => {
  await loadUsers({ page: 1, itemsPerPage: itemsPerPage.value, sortBy: [] });
});
</script>
