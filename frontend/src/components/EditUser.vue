<template>
  <v-card>
    <v-card-title class="white--text">
      Edição de Usuário
    </v-card-title>
    <v-card-text class="pa-6">
      <v-form
        :disabled="loading"
        @submit.prevent="salvarEditUser"
        ref="form"
        v-model="isValid"
      >
        <v-progress-linear
          v-if="loading"
          indeterminate
          class="mb-4"
        />

        <v-alert
          v-if="errorMessage"
          type="error"
          class="mb-4"
        >
          {{ errorMessage }}
        </v-alert>

        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="username"
              label="Nome de Usuário"
              :rules="[
                v => !!v || 'Nome de usuário é obrigatório'
              ]"
              required
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="email"
              label="E-mail"
              type="email"
              :rules="[
                v => !!v || 'E-mail é obrigatório',
                v => /.+@.+\..+/.test(v) || 'E-mail deve ser válido'
              ]"
              required
            />
          </v-col>

         <v-col cols="12" md="6">
            <v-select
              v-model="permissaoSelecionada"
              clearable
              label="Tipo de Acesso"
              :items="permissionOptions"
              item-title="text"
              item-value="value"
              :rules="[v => !!v || 'Tipo de acesso é obrigatório']"
              required
            />
          </v-col>
        </v-row>

        <v-card-actions class="pa-0 pt-4 justify-end">
          <v-btn
            color="red"
            @click="cancelar"
            :disabled="loading"
            class="mr-2"
          >
            <v-icon left>mdi-cancel</v-icon>
            Cancelar
          </v-btn>

          <v-btn
            type="submit"
            :disabled="!isValid || loading"
            color="green"
            :loading="loading"
          >
            <v-icon left>mdi-check</v-icon>
            Confirmar
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, watch } from "vue";

const emit = defineEmits(['close', 'saved']);

const props = defineProps({
  userToEdit: {
    type: Object,
    default: () => null
  }
});

const permissionOptions = [
  { text: 'Administrador', value: 'PROJECT_ADMIN' },
  { text: 'Gestor', value: 'PROJECT_MANAGER' },
  { text: 'Líder de Equipe', value: 'TEAM_LEADER' },
  { text: 'Membro de Equipe', value: 'TEAM_MEMBER' },
];

const username = ref('');
const email = ref('');
const loading = ref(false);
const isValid = ref(false);
const errorMessage = ref('');
const permissaoSelecionada = ref('');

watch(() => props.userToEdit, (newUser) => {
  if (newUser) {
    username.value = newUser.username || '';
    email.value = newUser.email || '';

    permissaoSelecionada.value = '';

    for (const permission of permissionOptions) {
      const hasPermission =
        (newUser.permissions && newUser.permissions[permission.value]) ||
        newUser[permission.value.toLowerCase()] ||
        newUser[permission.value] ||
        false;

      if (hasPermission) {
        permissaoSelecionada.value = permission.value;
        break;
      }
    }
  } else {
    limparFormulario();
  }
}, { immediate: true });

const getPermissionsObject = () => {
  const permissionsObj = {
    PROJECT_ADMIN: false,
    PROJECT_MANAGER: false,
    TEAM_LEADER: false,
    TEAM_MEMBER: false
  };

  if (permissaoSelecionada.value && permissionsObj.hasOwnProperty(permissaoSelecionada.value)) {
    permissionsObj[permissaoSelecionada.value] = true;
  }

  return permissionsObj;
};

const salvarEditUser = async () => {
  if (!isValid.value || loading.value) return;

  const permissions = getPermissionsObject();

  const requestBody = {
    username: username.value,
    email: email.value,
    permissions: permissions
  };

  loading.value = true;
  errorMessage.value = '';

  try {
    const response = await fetch(`/api/accounts/users/edit/${props.userToEdit.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
      credentials: 'include'
    });

    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = null;
    }

    if (!response.ok) {
      const errorMessage = errorData?.message || `Erro ${response.status}: ${response.statusText}`;
      throw new Error(errorMessage);    }

    emit('saved');
    emit('close');

  } catch (error) {
    console.error('Erro ao salvar usuário:', error);
    errorMessage.value = error.message || 'Erro ao salvar usuário. Tente novamente.';
  } finally {
    loading.value = false;
  }
}

const cancelar = () => {
  emit('close');
}

const limparFormulario = () => {
  username.value = '';
  email.value = '';
  permissaoSelecionada.value = '';
  errorMessage.value = '';
};
</script>
