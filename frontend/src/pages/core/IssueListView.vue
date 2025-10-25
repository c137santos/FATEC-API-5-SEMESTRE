<template>
  <v-container class="fill-height">
    <ListagemIssues />
  </v-container>
</template>

<script>
import { mapState } from "pinia"
import { useBaseStore } from "@/stores/baseStore"
import { usecoreStore } from "@/stores/coreStore"
import { useRoute } from "vue-router"
import ListagemIssues from "@/components/ListagemIssues.vue"

export default {
  name: "IssuesList",
  components: { ListagemIssues },
  setup() {
    const baseStore = useBaseStore()
    const coreStore = usecoreStore()
    const route = useRoute()

    const projectId = parseInt(route.params.id)
    const validProjectId = !isNaN(projectId) ? projectId : null;

    return { baseStore, coreStore, projectId: validProjectId }
  },
  computed: {
    ...mapState(usecoreStore, ["issues", "issuesLoading"]),
  },
  mounted() {
    this.getIssues()
  },
  methods: {
    getIssues() {
      if (this.projectId) {
         this.coreStore.getIssues(this.projectId)
      } else {
         console.error("ID do Projeto não encontrado na rota. Não será possível buscar as Issues.")
      }
    },

    async addNewIssue(issue) {
      const newIssue = await this.coreStore.addNewIssue(issue)
      this.baseStore.showSnackbar(`New issue added #${ newIssue.id }`)
      this.getIssues()
    },
  },
}
</script>

<style scoped>
.done {
  text-decoration: line-through;
}
</style>
