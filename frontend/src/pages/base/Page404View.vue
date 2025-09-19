<template>
  <v-container class="fill-height">
    <v-responsive class="d-flex align-center text-center fill-height">
      <v-issue>
        <v-issue-title class="headline">Opps!</v-issue-title>
        <v-issue-text> Não foi possível achar está página </v-issue-text>
        <v-issue-actions>
          <v-spacer />
          <v-btn color="primary" :to="{ name: 'base-home' }"> Início </v-btn>
        </v-issue-actions>
      </v-issue>
    </v-responsive>
  </v-container>
</template>

<script setup></script>
