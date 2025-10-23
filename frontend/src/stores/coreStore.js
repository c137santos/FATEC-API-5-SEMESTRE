import { defineStore } from "pinia"
import coreApi from "@/api/core.api.js"

export const usecoreStore = defineStore("coreStore", {
  state: () => ({
    issues: [],
    issuesLoading: false,
  }),
  actions: {
    async getIssues(projectId, page = 1) {
      this.issuesLoading = true
      const response = await coreApi.getIssues(projectId, page)
      this.issues = response.issues
      this.issuesLoading = false
    },
    async addNewIssue(tarefa) {
      const newIssue = await coreApi.addNewIssue(tarefa.title)
      return newIssue
    },
  },
})
