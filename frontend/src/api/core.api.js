import api from "./config.js"

export default {
  getIssues: async () => {
    const response = await api.get("/api/core/issues/list")
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
