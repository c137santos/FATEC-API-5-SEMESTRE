import api from "./config.js"

export default {
  getCards: async () => {
    const response = await api.get("/api/core/cards/list")
    return response.data
  },
  addNewCard: async (description) => {
    const json = { description }
    const response = await api.post(
      "/api/core/cards/add",
      json
    )
    return response.data
  },
}
