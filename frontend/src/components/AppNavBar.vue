<template>
  <v-app-bar app>
    <v-app-bar-nav-icon @click="drawer = !drawer" />

    <v-btn :to="{ name: 'overview'}"
     style=" margin-top:-40px;"
     class="btn-logo pa-0"
     ripple="false">
     
      <v-img
        src="@/assets/logo-jiboia.png"
        max-height="80"
        width="80"
      />
    </v-btn>

    <template #append>
      <v-btn
        :prepend-icon="theme === 'light' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
        @click.stop="themeClick"
      ></v-btn>
      <v-btn icon="mdi-account">
        <v-icon icon="mdi-account" />
        <v-menu activator="parent">
          <v-list>
            <v-list-item :to="{ name: 'accounts-logout' }">Sair</v-list-item>
          </v-list>
        </v-menu>
      </v-btn>
    </template>
  </v-app-bar>

  <v-navigation-drawer v-model="drawer" app>
    <v-list>
      <v-list-item to="/projects/overview">Overview</v-list-item>
      <v-list-item to="/user">Usuários</v-list-item>
    <v-list-group
      append-icon="mdi-chevron-down"
      no-action
    >
      <template #activator="{ props }">
        <v-list-item v-bind="props">
          <v-list-item-title>Projetos</v-list-item-title>
        </v-list-item>
      </template>
      <template v-if="projectList.length === 0">
      </template>
      <v-list-item
        v-for="project in projectList"
        :key="project.project_id"
        :to="`/projects/${project.project_id}`"
        link
      >
        <v-list-item-content>
          <v-list-item-title>{{ project.name }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list-group>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import { ref, onMounted } from 'vue'
import projectsApi from '@/api/projects.api'

export default {
  props: {
    title: {
      type: String,
      required: false,
      default: "Jiboia",
    },
    theme: {
      type: String,
      required: true,
      default: "dark",
    },
  },
  setup(props, { emit }) {
    const drawer = ref(false)
    const projectList = ref([])

    onMounted(async () => {
      try {
        const overview = await projectsApi.overview()
        projectList.value = overview.projects
      } catch (error) {
        console.error('Erro ao carregar projetos:', error)
      }
    })

    const themeClick = () => emit("themeClick")

    return { drawer, projectList, themeClick, title: props.title, theme: props.theme }
  },
}

</script>

<style>
.btn-logo .v-btn__overlay,
.btn-logo.v-btn--active .v-btn__overlay,
.btn-logo:active .v-btn__overlay {
  background: transparent !important;
}
.btn-logo,
.btn-logo.v-btn--active,
.btn-logo:active {
  background: transparent !important;
  box-shadow: none !important;
}
.btn-logo .v-ripple__container {
  display: none !important;
}
</style>
