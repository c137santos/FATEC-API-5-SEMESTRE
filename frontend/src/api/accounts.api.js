import api from "./config.js"

export default {
  whoami: async () => {
    const response = await api.get("/api/accounts/whoami")
    return response.data
  },
  login: async (username, password) => {
    const json = {username, password}
    const response = await api.post(
      "/api/accounts/login",
      json
    )
    return response.data
  },
  logout: async () => {
    const response = await api.post("/api/accounts/logout")
    return response.data
  },

  getUsers: async (page, limit, sortBy) => {
    const params = {};

    if (page) params.page = page;
    if (limit) params.limit = limit;
    if (sortBy && sortBy.length > 0) params.sortBy = sortBy.join(",");

    const response = await api.get("/api/accounts/users", { params });
    return response.data;
  }
}
