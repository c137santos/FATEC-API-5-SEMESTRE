import { defineStore } from "pinia"
import coreApi from "@/api/core.api.js"

export const usecoreStore = defineStore("coreStore", {
  state: () => ({
    issues: [],
    issuesLoading: false,
  }),
  actions: {
    async getIssues() {
      this.issuesLoading = true
      const response = await coreApi.getIssues()
      this.issues = response.issues
      this.issuesLoading = false
    },
    async addNewIssue(tarefa) {
      const newIssue = await coreApi.addNewIssue(tarefa.title)
      return newIssue
    },
  },
})
