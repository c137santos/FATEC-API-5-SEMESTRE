<template>
  <div class="d-flex justify-space-between align-center mb-4" style="width: 100%;">
    <h2>Users</h2> 
    <v-btn
      style="background-color: #172B4D; color: white"
      prepend-icon="mdi-account-plus"
      @click="abrirCadastro"
    >
      Cadastrar novo usuário
    </v-btn>
  </div>

  <v-container>
    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      :headers="headers"
      :items="users"
      :items-length="totalUsers"
      :loading="loading"
      @update:options="loadUsers"
    >
  
      <template v-slot:item.permissions="{ item }">
        <span>{{ formatarPermissao(item.permissions) }}</span>
      </template>

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

    <v-dialog v-model="dialogCadastro" max-width="800" persistent>
      <CadastrarUser
        @close="fecharCadastro"
        @saved="onUsuarioSalvo"
      />
    </v-dialog>

    <v-dialog v-model="dialogEdit" max-width="800" persistent>
      <EditUser
        :user-to-edit="userToEdit"
        @close="fecharEdit"
        @saved="onUsuarioSalvo"
      />
    </v-dialog>

    <v-dialog v-model="dialogDelete" max-width="600" persistent>
      <DeleteUser
        :user-to-delete="userToDelete"
        @close="fecharDelete"
        @deleted="onUsuarioDeletado"
      />
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import accountsApi from "@/api/accounts.api";
import CadastrarUser from "./CadastrarUser.vue";
import DeleteUser from "./DeleteUser.vue";
import EditUser from "./EditUser.vue";

const headers = ref([
  { title: "Id", key: "id", align: "start" },
  { title: "Nome", key: "username", align: "start" },
  { title: "E-mail", key: "email", align: "start" },
  { title: "Tipo de acesso", key: "permissions", align: "start" },
  { key: "actions", align: "center", sortable: false },
]);

const users = ref([]);
const itemsPerPage = ref(10);
const totalUsers = ref(0);
const loading = ref(true);
const dialogCadastro = ref(false);
const dialogDelete = ref(false);
const userToDelete = ref(null);
const dialogEdit = ref(false);
const userToEdit = ref(null);

const abrirCadastro = () => {
  dialogCadastro.value = true;
};

const fecharCadastro = () => {
  dialogCadastro.value = false;
};

const abrirDelete = (user) => {
  console.log('Deletar usuário:', user);
  userToDelete.value = user;
  dialogDelete.value = true;
};

const fecharDelete = () => {
  dialogDelete.value = false;
  userToDelete.value = null;
};

const abrirEdit = (user) => {
  console.log('Editar usuário:', user);
  userToEdit.value = user;
  dialogEdit.value = true;
};

const fecharEdit = () => {
  dialogEdit.value = false;
  userToEdit.value = null;
};

const onUsuarioSalvo = () => {
  fecharCadastro();
  fecharEdit();
  loadUsers({ page: 1, itemsPerPage: itemsPerPage.value });
};

const onUsuarioDeletado = () => {
  fecharDelete();
  loadUsers({ page: 1, itemsPerPage: itemsPerPage.value });
};

const searchUsers = async (page = 1, itemsPerPage = itemsPerPage.value) => {
  loading.value = true;

  try {
    const response = await accountsApi.getUsers(page, itemsPerPage);

    if (response.results && Array.isArray(response.results)) {
      users.value = response.results;
      totalUsers.value = response.count || 0;
    } else if (response.users && Array.isArray(response.users)) {
      users.value = response.users;
      totalUsers.value = response.total_items || 0;
    } else {
      users.value = [];
      totalUsers.value = 0;
    }

  } catch (error) {
    console.error("Erro ao buscar usuários:", error);
    users.value = [];
    totalUsers.value = 0;
  } finally {
    loading.value = false;
  }
};

const loadUsers = ({ page, itemsPerPage }) => {
  searchUsers(page, itemsPerPage);
};

onMounted(() => {
  loadUsers({ page: 1, itemsPerPage: itemsPerPage.value });
});

function formatarPermissao(perms) {
  if (!perms) return "-";
  const nomes = {
    PROJECT_ADMIN: "Administrador",
    PROJECT_MANAGER: "Gestor",
    TEAM_LEADER: "Líder de Equipe",
    TEAM_MEMBER: "Membro de Equipe"
  };
  const tipos = Object.entries(perms)
    .filter(([_, v]) => v)
    .map(([k]) => nomes[k] || k);
  return tipos.length ? tipos.join(', ') : 'Nenhum';
}
</script>
