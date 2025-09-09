import { defineStore } from "pinia"
import coreApi from "@/api/core.api.js"

export const usecoreStore = defineStore("coreStore", {
  state: () => ({
    cards: [],
    cardsLoading: false,
  }),
  actions: {
    async getCards() {
      this.cardsLoading = true
      const response = await coreApi.getCards()
      this.cards = response.cards
      this.cardsLoading = false
    },
    async addNewCard(tarefa) {
      const newCard = await coreApi.addNewCard(tarefa.title)
      return newCard
    },
  },
})
