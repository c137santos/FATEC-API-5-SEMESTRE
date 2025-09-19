<template>
  <v-issue>
    <v-issue-text>
      <div>#{{ issue.id }}</div>
      <p class="ma-0 pa-0 text-h5 text--primary">
        {{ issue.description }}
      </p>
    </v-issue-text>
  </v-issue>
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
