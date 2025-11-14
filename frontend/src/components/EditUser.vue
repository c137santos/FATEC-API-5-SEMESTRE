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

        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="nome"
              label="Nome Completo"
                :rules="[
                v => !!v || 'Nome é obrigatório'
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
import { ref, computed, watch } from "vue";

const emit = defineEmits(['close', 'saved']);

const props = defineProps({
  userToEdit: {
    type: Object,
    default: () => null
  }
});

const nome = ref('');
const email = ref('');
const tipoAcesso = ref('');
const loading = ref(false);
const form = ref(null);
const isValid = ref(false);

watch(() => props.userToEdit, (newUser) => {
  if (newUser) {
    nome.value = newUser.name || '';
    email.value = newUser.email || '';
    tipoAcesso.value = newUser.permissions || '';
  } else {
    limparFormulario();
  }
}, { immediate: true });

const valid = computed(() => {
  return nome.value &&
         email.value &&
         tipoAcesso.value
});

const salvarEditUser = async () => {
  if (!isValid.value || loading.value) return;

  const body = {
    id: props.userToEdit.id,
    name: nome.value,
    email: email.value,
    permissions: tipoAcesso.value,
  }

  loading.value = true;

  try {
    console.log('Atualizando usuário:', body);

    await new Promise(resolve => setTimeout(resolve, 1000));

    emit('saved');

  } catch (error) {
    console.error('Erro ao salvar usuário:', error);
  } finally {
    loading.value = false;
  }
}

const cancelar = () => {
  emit('close');
}

const limparFormulario = () => {
  nome.value = '';
  email.value = '';
  tipoAcesso.value = '';
};
</script>
