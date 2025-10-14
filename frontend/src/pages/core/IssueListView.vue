<template>
  <v-container class="fill-height">
    <ListagemIssues />
  </v-container>
</template>

<script>
import { mapState } from "pinia"
import { useBaseStore } from "@/stores/baseStore"
import { usecoreStore } from "@/stores/coreStore"
import Issue from "@/components/Issue.vue"
import IssueForm from "@/components/IssueForm.vue"
import ListagemIssues from "@/components/ListagemIssues.vue"

export default {
  name: "IssuesList",
  components: { Issue, IssueForm, ListagemIssues },
  setup() {
    const baseStore = useBaseStore()
    const coreStore = usecoreStore()
    return { baseStore, coreStore }
  },
  computed: {
    ...mapState(usecoreStore, ["issues", "issuesLoading"]),
  },
  mounted() {
    this.getIssues()
  },
  methods: {
    getIssues() {
      this.coreStore.getIssues()
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
