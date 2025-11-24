<template>
  <v-card>
    <v-card-title class="white--text">
      Cadastrar Novo Usuário
    </v-card-title>
    <v-card-text class="pa-6">
      <v-form
        :disabled="loading"
        @submit.prevent="salvarUser"
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
              :rules="[v => !!v || 'Nome de usuário é obrigatório']"
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
              v-model="permission"
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

        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="password"
              :type="mostrarSenha ? 'text' : 'password'"
              label="Senha"
              :rules="[
                v => !!v || 'Senha é obrigatória',
                v => (v && v.length >= 6) || 'Senha deve ter pelo menos 6 caracteres'
              ]"
              required
              :append-inner-icon="mostrarSenha ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append-inner="mostrarSenha = !mostrarSenha"
            />
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model="confirmPassword"
              :type="mostrarConfirmSenha ? 'text' : 'password'"
              label="Confirmar Senha"
              :rules="[
                v => !!v || 'Confirmação de senha é obrigatória',
                v => v === password || 'Senhas não coincidem'
              ]"
              required
              :append-inner-icon="mostrarConfirmSenha ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append-inner="mostrarConfirmSenha = !mostrarConfirmSenha"
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
            :disabled="!valid || loading"
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
import { ref, computed } from "vue";

const emit = defineEmits(['close', 'saved']);

const username = ref('')
const email = ref('')
const permission = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMessage = ref('')

const mostrarSenha = ref(false)
const mostrarConfirmSenha = ref(false)

const permissionOptions = [
  { text: 'Administrador', value: 'PROJECT_ADMIN' },
  { text: 'Gestor', value: 'PROJECT_MANAGER' },
  { text: 'Líder de Equipe', value: 'TEAM_LEADER' },
  { text: 'Membro de Equipe', value: 'TEAM_MEMBER' },
]

const valid = computed(() => {
  return username.value &&
         email.value &&
         permission.value &&
         password.value &&
         confirmPassword.value &&
         password.value === confirmPassword.value &&
         password.value.length >= 6;
});

const getCSRFToken = () => {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

const salvarUser = async () => {
  if (!valid.value) return;

  loading.value = true;
  errorMessage.value = '';

  const permissions = {
    PROJECT_ADMIN: permission.value === 'PROJECT_ADMIN',
    PROJECT_MANAGER: permission.value === 'PROJECT_MANAGER',
    TEAM_LEADER: permission.value === 'TEAM_LEADER',
    TEAM_MEMBER: permission.value === 'TEAM_MEMBER',
  };

  const body = {
    username: username.value,
    email: email.value,
    password: password.value,
    permissions: permissions,
  }

  try {
    const csrfToken = getCSRFToken();

    const headers = {
      'Content-Type': 'application/json',
    };

    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken;
    }

    const response = await fetch('/api/accounts/users/create', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(body),
      credentials: 'include'
    });

    const responseText = await response.text();

    if (!response.ok) {
      let errorMessage;
      try {
        const errorData = JSON.parse(responseText);
        errorMessage = errorData.message || errorData.error || `Erro ${response.status}: ${response.statusText}`;
      } catch {
        errorMessage = responseText || `Erro ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    let result;
    try {
      result = JSON.parse(responseText);
    } catch {
      result = responseText;
    }

    limparFormulario();
    emit('saved');

  } catch (error) {
    console.error('Erro ao criar usuário:', error);

    if (error.message.includes('CSRF') || error.message.includes('csrf')) {
      errorMessage.value = 'Erro de autenticação. Tente recarregar a página.';
    } else if (error.message.includes('403')) {
      errorMessage.value = 'Acesso negado. Verifique suas permissões.';
    } else {
      errorMessage.value = error.message || 'Erro ao criar usuário. Tente novamente.';
    }
  } finally {
    loading.value = false;
  }
}

const cancelar = () => {
  limparFormulario();
  emit('close');
}

const limparFormulario = () => {
  username.value = '';
  email.value = '';
  permission.value = '';
  password.value = '';
  confirmPassword.value = '';
  errorMessage.value = '';
}
</script>
