<template>
  <v-app-bar app>
    <v-app-bar-nav-icon @click="drawer = !drawer" />

    <v-app-bar-title>{{ title }}</v-app-bar-title>

    <template #append>
      <v-btn icon="mdi-heart" :to="{ name: 'overview' }"></v-btn>
      <v-btn icon="mdi-magnify"></v-btn>
      <v-btn
        :prepend-icon="theme === 'light' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
        @click.stop="themeClick"
      ></v-btn>

      <v-btn icon="mdi-dots-vertical">
        <v-icon icon="mdi-dots-vertical" />
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
      <v-list-item to="/accounts/users">Usuários</v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
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
  emits: ["themeClick"],
  data: () => ({
    drawer: false,
  }),
  methods: {
    themeClick() {
      this.$emit("themeClick")
    },
  },
}
</script>
