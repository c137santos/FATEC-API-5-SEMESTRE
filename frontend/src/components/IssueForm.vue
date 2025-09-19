<template>
  <div>
    <v-issue>
      <v-issue-text>
        <v-text-field
          v-model="title"
          :label="formLabel"
          required
          outlined
          append-icon="fa-pen"
          @keyup.enter="addNewIssue" />
      </v-issue-text>
    </v-issue>
  </div>
</template>

<script>
export default {
  props: {
    formLabel: {
      type: String,
      default: "",
    },
  },
  emits: ["newIssue"],
  data: () => {
    return {
      title: "",
    }
  },
  methods: {
    addNewIssue() {
      this.$emit("newIssue", {
        title: this.title,
      })
      this.title = ""
    },
  },
}
</script>

<style scoped></style>
