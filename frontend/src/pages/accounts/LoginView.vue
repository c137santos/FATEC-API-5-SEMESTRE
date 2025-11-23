<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center" no-gutters>
      <v-col cols="12" sm="8" md="5" lg="4">
        
        <v-card 
          class="pa-8 bg-grey-darken-3" 
          rounded="xl" 
          elevation="12"
        >
          <div class="d-flex justify-center mb-6">
            <v-avatar color="primary" size="80" class="elevation-6">
              <v-icon icon="mdi-account" size="40" color="white"></v-icon>
            </v-avatar>
          </div>

          <h1 class="text-h4 font-weight-bold text-center mb-2">Bem-vindo</h1>
          <p class="text-body-2 text-medium-emphasis text-center mb-8">
            Entre com suas credenciais para continuar
          </p>

          <v-form @submit.prevent="login">
            <v-text-field
              v-model="username"
              label="Usuário"
              prepend-inner-icon="mdi-account-outline"
              variant="outlined"
              color="primary"
              class="mb-2"
              required
            ></v-text-field>

            <v-text-field
              v-model="password"
              type="password"
              label="Senha"
              prepend-inner-icon="mdi-lock-outline"
              variant="outlined"
              color="primary"
              class="mb-6"
              required
            ></v-text-field>

            <v-btn
              block
              size="x-large"
              rounded="pill"
              color="primary"
              class="font-weight-bold mb-4"
              elevation="4"
              type="submit"
            >
              Entrar
              <v-icon icon="mdi-chevron-right" end></v-icon>
            </v-btn>

            <v-divider class="my-4 text-medium-emphasis">ou</v-divider>

            <v-btn
              block
              size="large"
              rounded="pill"
              variant="tonal"
              color="white"
              :to="{ name: 'base-home' }"
            >
              Voltar ao Início
            </v-btn>
          </v-form>
        </v-card>

      </v-col>
    </v-row>
  </v-container>
</template>
<script>
import { mapState } from "pinia"
import { useBaseStore } from "@/stores/baseStore"
import { useAccountsStore } from "@/stores/accountsStore"

export default {
  setup() {
    const baseStore = useBaseStore()
    const accountsStore = useAccountsStore()
    return { baseStore, accountsStore }
  },
  data: () => {
    return {
      valid: false,
      username: "",
      password: "",
    }
  },
  computed: {
    ...mapState(useAccountsStore, ["loggedUser"]),
  },
  async mounted() {
    console.log(this.loggedUser)
    await this.accountsStore.whoAmI()
    if (this.loggedUser) {
      this.baseStore.showSnackbar("Usuário já logado", "warning")
      this.showIssues()
    }
  },
  methods: {
    async login() {
      const user = await this.accountsStore.login(this.username, this.password)
      if (!user) {
        this.baseStore.showSnackbar("Usuário ou senha invalida", "danger")
        return
      }
      console.log("logged")
      this.showIssues()
    },
    showIssues() {
      this.$router.push({ path: "/projects/overview" })
      console.log("--> issues")
    },
  },
}
</script>

<script>
import { mapState } from "pinia"
import { useBaseStore } from "@/stores/baseStore"
import { useAccountsStore } from "@/stores/accountsStore"

export default {
  setup() {
    const baseStore = useBaseStore()
    const accountsStore = useAccountsStore()
    return { baseStore, accountsStore }
  },
  data: () => {
    return {
      valid: false,
      username: "",
      password: "",
    }
  },
  computed: {
    ...mapState(useAccountsStore, ["loggedUser"]),
  },
  async mounted() {
    console.log(this.loggedUser)
    await this.accountsStore.whoAmI()
    if (this.loggedUser) {
      this.baseStore.showSnackbar("Usuário já logado", "warning")
      this.showIssues()
    }
  },
  methods: {
    async login() {
      const user = await this.accountsStore.login(this.username, this.password)
      if (!user) {
        this.baseStore.showSnackbar("Usuário ou senha invalida", "error")
        return
      }
      console.log("logged")
      this.showIssues()
    },
    showIssues() {
      this.$router.push({ path: "/projects/overview" })
      console.log("--> issues")
    },
  },
}
</script>