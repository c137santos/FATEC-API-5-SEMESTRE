<template>
	<v-sheet 
	class="mx-auto mt-12"
	max-width="800"
	elevation="8"
	>
		<st-easter-egg code="konami">
			<div style="position: fixed; z-index: 1000; left: -8px; top: 50px"><img src="@/assets/Group 22.png" alt="Easter Egg" /></div>
		</st-easter-egg>
		<v-container>
			<v-row>
				<v-col>
					<h2> Projects Overview </h2>
				</v-col>
		 </v-row>
		 <v-row>
			<v-col>
				<v-container>
					<v-row class="mx-100 d-flex justify-center"> Selecionar Projeto </v-row>
					<v-row>
						<v-slide-group show-arrows>
							<v-slide-group-item v-for="(project, i) in projectList" :key="i" v-slot="{ isSelected, toggle }">
								<v-btn
									:color="isSelected ? 'primary' : undefined"
									class="ma-2"
									@click="toggle"
								> {{ project.name }} </v-btn>
							</v-slide-group-item>
						</v-slide-group>
					</v-row>
				</v-container>
			</v-col>
		 </v-row>
		 <v-row>
			<v-col>
				<div class="bg-grey w-100" style="height: 362px;"></div>
			</v-col>
		 </v-row>
		 <div :key="projectList.map(p => p.id).join()">
			 <v-row>
				<v-col>
					<span class="w-100 d-flex justify-center">Horas por projeto</span>
					<Bar
						:data="perHourData"
						:options="{
							responsive: true,
							indexAxis: 'y',
						}"
					></Bar>
				</v-col>
				<v-col>
					<span class="w-100 d-flex justify-center">Issues por projeto</span>
					<Doughnut
						:data="perIssuesData"
						:options="{
							responsive: true,
						}"
					></Doughnut>
				</v-col>
			 </v-row>
		 </div>
		</v-container>
	</v-sheet>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import projectsApi from '@/api/projects.api'
import { chartColors } from '@/utils/chart-utils'

const projectList = ref([])

const perHourData = computed(() => ({
	labels: projectList.value.map(project => project.name),
	datasets: [
		{
			label: 'Horas',
			borderWidth: 2,
			data: projectList.value.map(project => project.total_hours),
			backgroundColor: chartColors[3],
		}
	]
}))

const perIssuesData = computed(() => ({
	labels: projectList.value.map(project => project.name),
	datasets: [
		{
			label: 'Issues',
			data: projectList.value.map(project => project.total_issues),
			borderColor: 'rgba(255, 255, 255, 0)',
			backgroundColor: chartColors,
		}
	]
}))

onMounted(async () => {
	projectList.value = await projectsApi.list()
})

</script>