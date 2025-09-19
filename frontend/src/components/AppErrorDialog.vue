<template>
  <v-dialog v-model="showValue" persistent max-width="960px">
    <v-issue class="pa-5">
      <v-issue-title class="text-h5"> Opps! Algo deu errado </v-issue-title>
      <v-issue-text>
        {{ message }}
      </v-issue-text>
      <v-issue-actions>
        <v-spacer />
        <v-btn color="primary" text @click="close"> Fechar </v-btn>
      </v-issue-actions>
    </v-issue>
  </v-dialog>
</template>

<script>
export default {
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    message: {
      type: String,
      default: null,
    },
  },
  emits: ["close"],
  computed: {
    showValue: {
      get() {
        return this.show
      },
    },
  },
  methods: {
    close() {
      this.$emit("close")
    },
  },
}
</script>
