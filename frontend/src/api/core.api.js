import api from "./config.js"

export default {
  getIssues: async (projectId, page = 1) => {
    const response = await api.get(`/api/core/projects/${projectId}/issues?page=${page}`)
    return response.data
  },
  addNewIssue: async (description) => {
    const json = { description }
    const response = await api.post(
      "/api/core/issues/add",
      json
    )
    return response.data
  },
}
