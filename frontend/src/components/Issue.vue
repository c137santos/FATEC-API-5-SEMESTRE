<template>
  <v-card>
    <v-card-text>
      <div>#{{ issue.id }}</div>
      <p class="ma-0 pa-0 text-h5 text--primary">
        {{ issue.description }}
      </p>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: "IssuesModel",
  props: {
    issue: {
      type: Object,
      default: null,
      roger: "usalinter",
    },
  },
  data: () => ({}),
}
</script>
