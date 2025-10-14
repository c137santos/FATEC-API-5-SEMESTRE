<template>
  <div class="text-h2 ma-2 pa-2">Issues</div>

  <v-container class="d-flex justify-center align-center">
    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      :headers="headers"
      :items="issues"
      :items-length="totalIssues"
      :loading="loading"
      item-value="id"
      @update:options="loadIssues"
      class="rounded-lg elevation-5 bg-deep-purple-lighten-5"
    >

      <template v-slot:item.author="{ item }">
          {{ item.user_related?.user_name || 'N/A' }}
      </template>

      <template v-slot:item.timeCreated="{ item }">
        {{ formatDate(item.created_at) }}
      </template>

      <template v-slot:no-data>
        <div class="text-center pa-4">Nenhuma issue encontrada.</div>
      </template>
    </v-data-table-server>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const headers = ref([
  { title: "Issue ID", key: "jira_id", align: "start" },
  { title: "Issue Summary", key: "description", align: "start" },
  { title: "Author", key: "author", align: "start" }, 
  { title: "Time Created", key: "timeCreated", align: "start" },
]);

const issues = ref([]);
const itemsPerPage = ref(10);
const totalIssues = ref(0);
const loading = ref(true);

const searchIssues = async (page = 1) => {
  loading.value = true;

  try {
    const response = await axios.get(
      `/api/core/issues?page=${page}`
    );

    const data = response.data;
    issues.value = data.issues || [];
    totalIssues.value = data.total_items || 0; 
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

onMounted(() => {
  searchIssues(1);
});
</script>