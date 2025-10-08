<template>
  <div>
    <v-btn style="background-color: #172B4D; color: white" @click="executarCron">
      Atualizar Dados
    </v-btn>
  </div>
</template>

<script setup>
import axios from "axios";
import { ref } from "vue";

const executarCron = async () => {
    try{
        const response = await axios.post("/api/core/btncron-all")
        console.log(response.data)
    } catch (error) {
        console.log(error);
    }
}
</script>