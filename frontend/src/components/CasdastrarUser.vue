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

        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="nome"
              label="Nome Completo"
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
            <v-combobox
              v-model="tipoAcesso"
              clearable
              label="Tipo de Acesso"
              :items="['Administrador', 'Gestor', 'Desenvolvedor']"
              :rules="[v => !!v || 'Tipo de acesso é obrigatório']"
              required
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="senha"
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
              v-model="confirmSenha"
              :type="mostrarConfirmSenha ? 'text' : 'password'"
              label="Confirmar Senha"
              :rules="[
                v => !!v || 'Confirmação de senha é obrigatória',
                v => v === senha || 'Senhas não coincidem'
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

const nome = ref('')
const email = ref('')
const tipoAcesso = ref('')
const senha = ref('')
const confirmSenha = ref('')
const loading = ref(false)

const mostrarSenha = ref(false)
const mostrarConfirmSenha = ref(false)

const valid = computed(() => {
  return nome.value &&
         email.value &&
         tipoAcesso.value &&
         senha.value &&
         confirmSenha.value &&
         senha.value === confirmSenha.value &&
         senha.value.length >= 3;
});

const salvarUser = async () => {
  if (!valid.value) return;

  const body = {
    nome: nome.value,
    email: email.value,
    tipoAcesso: tipoAcesso.value,
    senha: senha.value,
    confirmSenha: confirmSenha.value,
  }

  loading.value = true;

  try {
    console.log('Salvando usuário:', body);

    await new Promise(resolve => setTimeout(resolve, 1000));

    limparFormulario();

    emit('saved');

  } catch (error) {
    console.error('Erro ao salvar usuário:', error);
  } finally {
    loading.value = false;
  }
}

const cancelar = () => {
  limparFormulario();
  emit('close');
}

const limparFormulario = () => {
  nome.value = '';
  email.value = '';
  tipoAcesso.value = '';
  senha.value = '';
  confirmSenha.value = '';
}
</script>
