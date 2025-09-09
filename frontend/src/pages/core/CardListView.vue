<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12">
        <v-card>
          <v-card-title class="headline"> Cards </v-card-title>
        </v-card>
      </v-col>

      <v-col cols="12">
        <card-form :form-label="'New Card'" @new-card="addNewCard" />
      </v-col>

      <v-col v-for="item in cards" :key="item.id" cols="12">
        <card :card="item" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapState } from "pinia"
import { useBaseStore } from "@/stores/baseStore"
import { usecoreStore } from "@/stores/coreStore"
import Card from "@/components/Card.vue"
import CardForm from "@/components/CardForm.vue"

export default {
  name: "CardsList",
  components: { Card, CardForm },
  setup() {
    const baseStore = useBaseStore()
    const coreStore = usecoreStore()
    return { baseStore, coreStore }
  },
  computed: {
    ...mapState(usecoreStore, ["cards", "cardsLoading"]),
  },
  mounted() {
    this.getCards()
  },
  methods: {
    getCards() {
      this.coreStore.getCards()
    },
    async addNewCard(card) {
      const newCard = await this.coreStore.addNewCard(card)
      this.baseStore.showSnackbar(`New card added #${ newCard.id }`)
      this.getCards()
    },
  },
}
</script>

<style scoped>
.done {
  text-decoration: line-through;
}
</style>
