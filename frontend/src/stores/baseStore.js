import { defineStore } from "pinia"

export const useBaseStore = defineStore("baseStore", {
  state: () => ({
    errorMessage: undefined,
    showErrorMessage: false,
    snackbarMessage: undefined,
    showSnackbarMessage: false,
    type: "success",
  }),
  actions: {
    setShowErrorMessage(errorMessage) {
      this.errorMessage = errorMessage
      this.showErrorMessage = !!errorMessage
    },
    showSnackbar(message, type, options = {}) {
      this.type = type
      this.snackbarMessage = message
      this.showSnackbarMessage = true

      // Se um timeout for passado nas opções, usa-o para esconder o snackbar
      if (options.timeout && options.timeout > 0) {
        setTimeout(() => {
          this.hideSnackbar()
        }, options.timeout)
      }
    },
    hideSnackbar() {
      this.showSnackbarMessage = false
      this.snackbarMessage = undefined
    },
  },
})