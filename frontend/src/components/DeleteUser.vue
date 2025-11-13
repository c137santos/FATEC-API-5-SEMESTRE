<template>
  <v-card>
    <v-card-text class="pa-6">
      <v-form
        :disabled="loading"
        @submit.prevent="deleteUser"
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
            <div class="text-h5 mb-4">
              Tem certeza que deseja deletar o usuário
              <strong>{{ userToDelete?.name || userToDelete?.username }}</strong>?
            </div>
            <div class="text-body-1 text-grey">
              Esta ação não pode ser desfeita.
            </div>
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
            :disabled="loading"
            color="green"
            :loading="loading"
          >
            <v-icon left>mdi-check</v-icon>
            Deletar
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  userToDelete: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'deleted']);

const loading = ref(false);
const errorMessage = ref('');

const valid = computed(() => {
  return props.userToDelete !== null;
});

const deleteUser = async () => {
  if (!valid.value) return;

  loading.value = true;
  errorMessage.value = '';

  try {
    console.log('Deletando usuário:', props.userToDelete);

    await new Promise(resolve => setTimeout(resolve, 1000));

    console.log('Usuário deletado com sucesso');
    emit('deleted');

  } catch (error) {
    console.error('Erro ao deletar usuário:', error);
    errorMessage.value = error.message || 'Erro ao deletar usuário. Tente novamente.';
  } finally {
    loading.value = false;
  }
}

const cancelar = () => {
  emit('close');
}
</script>
