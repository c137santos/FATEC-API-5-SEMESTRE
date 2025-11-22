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
              Tem certeza que deseja desativar o usuário
              <strong>{{ userDisplayName }}</strong>?
            </div>
            <div class="text-body-1 text-grey">
              Tem certeza que deseja desativar este usuário? Esta ação não pode ser desfeita.
            </div>
          </v-col>
        </v-row>

        <v-card-actions class="pa-0 pt-4 justify-end">
          <v-btn
            color="grey"
            @click="cancelar"
            :disabled="loading"
            class="mr-2"
          >
            <v-icon left>mdi-cancel</v-icon>
            Cancelar
          </v-btn>

          <v-btn
            type="submit"
            :disabled="loading || !valid"
            color="red"
            :loading="loading"
          >
            <v-icon left>mdi-delete</v-icon>
            Desativar Usuário
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
  return props.userToDelete !== null && props.userToDelete.id;
});

const userDisplayName = computed(() => {
  if (!props.userToDelete) return '';
  return props.userToDelete.name || props.userToDelete.username || props.userToDelete.email || 'Usuário';
});

const deleteUser = async () => {
  loading.value = true;
  errorMessage.value = '';

  try {
    const response = await fetch(`/api/accounts/users/${props.userToDelete.id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include'
    });

    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = null;
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    emit('deleted');
    emit('close');

  } catch (error) {
    console.error('Erro ao deletar usuário:', error);
    errorMessage.value = error.message || 'Erro ao deletar usuário. Tente novamente.';
  }
}

const cancelar = () => {
  emit('close');
}
</script>
