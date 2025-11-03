<template>
  <v-container class="fill-height">
    <ListagemUsers />
  </v-container>
</template>

<script>
import ListagemUsers from "@/components/ListagemUsers.vue"

export default {
  name: "UsersList",
  components: { ListagemUsers },
}
</script>

<style scoped>
.done {
  text-decoration: line-through;
}
</style>
