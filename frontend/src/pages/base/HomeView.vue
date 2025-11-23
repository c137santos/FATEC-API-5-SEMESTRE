<template>
  <v-container fluid class="fill-height pa-0 position-relative overflow-hidden">
    
    <!-- BACKGROUND SHAPE (A ONDA AZUL) -->
    <div class="background-shape">
       <svg viewBox="0 0 500 800" preserveAspectRatio="none" class="wave-svg">
          <!-- Curva suave "S" para criar o efeito split-screen orgânico -->
          <path d="M120,0 C260,200 -20,400 100,800 L500,800 L500,0 Z" 
                style="stroke: none; fill: rgb(var(--v-theme-primary));">
          </path>
       </svg>
    </div>

    <v-row no-gutters class="fill-height">
      
      <!-- LADO ESQUERDO: Conteúdo Textual -->
      <v-col cols="12" md="6" class="d-flex align-center justify-center justify-md-start px-8 px-lg-16 position-relative" style="z-index: 10;">
        <div style="max-width: 600px;">
          
          <h1 class="text-h3 text-lg-h2 font-weight-black mb-6 text-high-emphasis lh-tight">
            Bem vindo ao <span class="text-primary">Jiboia!</span>
          </h1>

          <p class="text-h6 text-medium-emphasis font-weight-regular mb-10" style="line-height: 1.6;">
            Simplifique o acompanhamento de projetos conectando-se diretamente ao Jira. 
            Transforme tarefas em dashboards visuais para uma visão completa sobre andamento, performance e esforço da equipe.
          </p>

          <div>
            <v-btn
              v-if="!loggedUser"
              :to="{ name: 'accounts-login' }"
              color="primary"
              size="x-large"
              height="60"
              min-width="200"
              rounded="pill"
              class="text-uppercase font-weight-bold btn-glow px-8"
              elevation="8"
            >
              Fazer Login
              <v-icon icon="mdi-arrow-right" end class="ml-2" />
            </v-btn>

            <v-btn
              v-else
              :to="{ name: 'issues-list' }"
              color="primary"
              size="x-large"
              height="60"
              min-width="200"
              rounded="pill"
              class="text-uppercase font-weight-bold btn-glow px-8"
              elevation="8"
            >
              Ir para o Sistema
              <v-icon icon="mdi-view-dashboard" end class="ml-2" />
            </v-btn>
          </div>
          
        </div>
      </v-col>

      <!-- LADO DIREITO: Logo Flutuante -->
      <v-col cols="12" md="6" class="d-none d-md-flex align-center justify-center position-relative" style="z-index: 5;">
        <div class="logo-container">
            <v-img 
              src="@/assets/logo-jiboia.png" 
              width="450"
              class="logo-float"
              contain
            />
        </div>
      </v-col>

    </v-row>
  </v-container>
</template>

<script>
import { mapState } from "pinia"
import { useAccountsStore } from "@/stores/accountsStore"

export default {
  name: 'HomeView',
  computed: {
    ...mapState(useAccountsStore, ["loggedUser"]),
  },
}
</script>

<style scoped>
/* Configuração da Onda Lateral */
.background-shape {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  /* Largura dinâmica: ocupa mais da metade da tela em telas largas */
  width: 55vw; 
  height: 100vh;
  z-index: 1;
  pointer-events: none; /* Garante que cliques passem através da área transparente do SVG se necessário */
}

.wave-svg {
  width: 100%;
  height: 100%;
  display: block;
  /* Garante que o SVG cubra a área sem distorção indesejada */
  object-fit: cover; 
}

/* Animação do Logo */
.logo-float {
  filter: drop-shadow(0 25px 50px rgba(0,0,0,0.2));
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
  100% { transform: translateY(0px); }
}

/* Efeitos do Botão */
.btn-glow {
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-glow:hover {
  transform: translateY(-2px);
  /* Sombra azulada brilhante ao passar o mouse */
  box-shadow: 0 10px 30px -5px rgba(var(--v-theme-primary), 0.5) !important;
}

.lh-tight {
  line-height: 1.1 !important;
}
</style>