<template>
  <div class="text-h2 ma-2 pa-2">Issues</div>

  <v-container class="d-flex justify-center align-center">
    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      :headers="headers"
      :items="issues"
      :items-length="totalIssues"
      :loading="loading"
      @update:options="loadIssues"
    >

      <template v-slot:item.actions="{ item }">
        <v-btn
          icon
          variant="text"
          color="black"
          @click="abrirDialog(item)"
        >
          <v-icon>mdi-eye</v-icon>
        </v-btn>
      </template>

      <template v-slot:item.author="{ item }">
          {{ item.user_related?.user_name || 'Não foi encontrado ou não existe autor para essa issue' }}
      </template>

      <template v-slot:item.timeCreated="{ item }">
        {{ formatDate(item.created_at) }}
      </template>

      <template v-slot:no-data>
        <div class="text-center pa-4">Nenhuma issue encontrada.</div>
      </template>
    </v-data-table-server>

    <PopUpIssue
      v-model:abrir="dialogAberto"
      :issue="issueSelecionada"
      @close="dialogAberto = false"
    />
  </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import coreApi from '@/api/core.api.js'
import PopUpIssue from './PopUpIssue.vue';

const headers = ref([
  { title: "Id da Issue", key: "jira_id", align: "start" },
  { title: "Sumário issue ", key: "description", align: "start" },
  { title: "Autor", key: "author", align: "start" },
  { title: "Data de criação", key: "timeCreated", align: "start" },
  { key: "actions", align: "center", sortable: false },
]);

const issues = ref([]);
const itemsPerPage = ref(10);
const totalIssues = ref(0);
const loading = ref(true);
const dialogAberto = ref(false);
const issueSelecionada = ref(null);

const abrirDialog = (issue) => {
  issueSelecionada.value = issue;
  dialogAberto.value = true;
};

const searchIssues = async (page = 1) => {
  loading.value = true;

  try {
    const response = await coreApi.getIssues(page);

    issues.value = response.issues || [];
    totalIssues.value = response.total_items || 0;

  } catch (error) {
    console.error("Erro ao buscar issues:", error);
    issues.value = [];
    totalIssues.value = 0;
  } finally {
    loading.value = false;
  }
}

const loadIssues = (options) => {
  const page = options?.page ?? 1;
  searchIssues(page);
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';

  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR');
  } catch {
    return dateString;
  }
}

onMounted(async () => {
  searchIssues(1);
});
</script>
