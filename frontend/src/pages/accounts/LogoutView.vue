<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center" no-gutters>
      <v-col cols="12" sm="8" md="5" lg="4">
        
        <v-card 
          class="pa-8 bg-grey-darken-3 text-center" 
          rounded="xl" 
          elevation="12"
        >
          <!-- Ícone de Destaque (Power Off) -->
          <div class="d-flex justify-center mb-6">
            <v-avatar color="primary" size="80" class="elevation-6">
              <v-icon icon="mdi-power" size="40" color="white"></v-icon>
            </v-avatar>
          </div>

          <h2 class="text-h4 font-weight-bold mb-2">Já vai?</h2>
          
          <p class="text-body-1 text-medium-emphasis mb-8">
            Tem certeza que deseja finalizar sua sessão atual?
          </p>

          <!-- Botão Logout (Ação Principal) -->
          <v-btn
            block
            size="x-large"
            rounded="pill"
            color="primary"
            class="font-weight-bold mb-4"
            elevation="4"
            :loading="loading"
            @click="logout"
          >
            Sim, Sair
          </v-btn>

          <!-- Botão Cancelar -->
          <v-btn
            block
            size="large"
            rounded="pill"
            variant="tonal"
            color="white"
            @click="cancel"
          >
            Cancelar
          </v-btn>

        </v-card>

      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useAccountsStore } from "@/stores/accountsStore"

export default {
  setup() {
    const accountsStore = useAccountsStore()
    return { accountsStore }
  },
  data() {
    return {
      loading: false,
    }
  },
  methods: {
    async logout() {
      this.loading = true
      try {
        await this.accountsStore.logout()
        this.$router.push({ name: 'base-home' })
      } catch (error) {
        console.error("Erro ao sair", error)
        this.baseStore.showSnackbar("Ocorreu um erro ao tentar sair.", "error", { timeout: 2000 })
      } finally {
        this.loading = false
      }
    },
    cancel() {
      this.$router.push({ name: 'overview' }) 
    }
  },
}
</script>