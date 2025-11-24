import { defineStore } from "pinia"

export const useBaseStore = defineStore("baseStore", {
  state: () => ({
    errorMessage: undefined,
    showErrorMessage: false,
    snackbarMessage: undefined,
    showSnackbarMessage: false,
    type: "success",
    snackbarTimeout: 2000
  }),
  actions: {
    setShowErrorMessage(errorMessage) {
      this.errorMessage = errorMessage
      this.showErrorMessage = !!errorMessage
    },
    showSnackbar(message, type = "success", options = {}) {
        this.type = type
        this.snackbarMessage = typeof message === 'string' ? message : undefined
        this.showSnackbarMessage = true
        
        // Definir timeout: usa o passado ou padrão
        this.snackbarTimeout = (options.timeout && options.timeout > 0) ? options.timeout : 2000

        // Garantir fechamento automático
        setTimeout(() => {
          this.hideSnackbar()
        }, this.snackbarTimeout)
      },
    hideSnackbar() {
      this.showSnackbarMessage = false
      this.snackbarMessage = undefined
    },
  },
})