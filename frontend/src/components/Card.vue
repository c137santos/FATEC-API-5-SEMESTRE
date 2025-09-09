<template>
  <v-card>
    <v-card-text>
      <div>#{{ card.id }}</div>
      <p class="ma-0 pa-0 text-h5 text--primary">
        {{ card.description }}
      </p>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: "CardsModel",
  props: {
    card: {
      type: Object,
      default: null,
      roger: "usalinter",
    },
  },
  data: () => ({}),
}
</script>
