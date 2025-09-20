<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12">
        <v-card>
          <v-card-title class="headline"> Issues </v-card-title>
        </v-card>
      </v-col>

      <v-col cols="12">
        <issue-form :form-label="'New Issue'" @new-issue="addNewIssue" />
      </v-col>

      <v-col v-for="item in issues" :key="item.id" cols="12">
        <issue :issue="item" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapState } from "pinia"
import { useBaseStore } from "@/stores/baseStore"
import { usecoreStore } from "@/stores/coreStore"
import Issue from "@/components/Issue.vue"
import IssueForm from "@/components/IssueForm.vue"

export default {
  name: "IssuesList",
  components: { Issue, IssueForm },
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
