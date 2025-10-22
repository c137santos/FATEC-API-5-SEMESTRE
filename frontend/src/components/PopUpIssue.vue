<template>
  <v-dialog v-model="props.abrir" max-width="500">
    <v-card>
      <v-card-title class="text-h6">Detalhes da Issue</v-card-title>
      <v-card-text>
        <v-form>
          <v-text-field v-model="infoIssue.idIssue" label="ID da Issue" readonly disabled />
          <v-text-field v-model="infoIssue.timeCreated" label="Data de Criação" readonly disabled />
          <v-text-field v-model="infoIssue.tituloIssue" label="Título" readonly disabled />
          <v-textarea v-model="infoIssue.descricao" label="Descrição" readonly disabled />
          <v-text-field v-model="infoIssue.autor" label="Autor" readonly disabled />
          <v-text-field v-model="infoIssue.timeSpent" label="Tempo Gasto (h)" readonly disabled />
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-btn block color="red-darken-1" variant="flat" @click="botaoFechar">Fechar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  abrir: Boolean,
  issue: Object,
});

const emit = defineEmits(["update:abrir", "close"]);

const formatDate = (dateStr) => {
  try {
    return new Date(dateStr).toISOString().split("T")[0];
  } catch {
    return dateStr;
  }
};

const infoIssue = computed(() => ({
  idIssue: props.issue?.jira_id || "",
  timeCreated: formatDate(props.issue?.created_at) || "",
  tituloIssue: props.issue?.description || "",
  descricao: props.issue?.details || "",
  autor: props.issue?.user_related?.user_name || "—",
  timeSpent: props.issue?.time_spend_hours || "0",
}));

const botaoFechar = () => {
  emit("update:abrir", false);
  emit("close");
};
</script>
