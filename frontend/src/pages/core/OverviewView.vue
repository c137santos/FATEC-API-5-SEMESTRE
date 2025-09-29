<template>
	<v-sheet 
		class="mx-auto my-8 bg-transparent"
		max-width="1400"
	>
		<DashboardLayout>
				<template #easter-egg>
					<img src="@/assets/Group 22.png" alt="Easter Egg" />
				</template>
				<template #title> Project Overview </template>
				<v-container :key="projectList.map(p => p.id).join()">
					<v-row>
						<v-col>
							<v-container>
								<v-row class="mx-100 d-flex justify-center"> Selecionar Projeto </v-row>
								<v-row>
									<v-slide-group show-arrows>
										<v-slide-group-item v-for="(project, i) in projectList" :key="i">
											<v-btn
												class="ma-2"
												@click="() => { router.push({ path: `/projects/${project.project_id}` }) }"
											> {{ project.name }} </v-btn>
										</v-slide-group-item>
									</v-slide-group>
								</v-row>
							</v-container>
						</v-col>
					</v-row>
					<v-row>
						<v-col>
							<span class="w-100 d-flex justify-center">Horas de desenvolvedores</span>
							<Bar
								:data="devProjectData"
								:options="{
									responsive: true,
									scales: {
										x: {
											stacked: true,
										},
										y: {
											stacked: true,
										}
									}
								}"
							></Bar>
						</v-col>
						<v-col>
							<span class="w-100 d-flex justify-center">Movimentação de issues (por mês)</span>
							<StatusBreakdownGraph v-model="issuesList"></StatusBreakdownGraph>
						</v-col>
					</v-row>
					<v-row>
					 <v-col class="">
						 <span class="w-100 d-flex justify-center">Horas por projeto</span>
						 <div>
							 <Bar
								 :data="perHourData"
								 :options="{
									 responsive: true,
									 indexAxis: 'y',
									 plugins: {
										 legend: {
											 display: false,
										 }
									 }
								 }"
							 ></Bar>
						 </div>
					 </v-col>
					 <v-col>
						 <div class="h-100 d-flex flex-column ga-4">
							 <span class="w-100 d-flex justify-center">Issues por projeto</span>
							 <div class="flex-grow-1">
								 <Doughnut
									 :data="perIssuesData"
									 :options="{
										 responsive: true,
										 aspectRatio: false,
										 plugins: {
											 legend: {
												 position: 'right'
											 }
										 }
									 }"
								 ></Doughnut>
							 </div>
						 </div>
					 </v-col>
					</v-row>
				</v-container>
		</DashboardLayout>
	</v-sheet>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import projectsApi from '@/api/projects.api'
import { chartColors } from '@/utils/chart-utils'
import StatusBreakdownGraph from '@/components/StatusBreakdownGraph'
import DashboardLayout from '@/layouts/default/DashboardLayout.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const projectList = ref([])
const devList = ref([])
const issuesList = ref([])

const perHourData = computed(() => ({
	labels: projectList.value.map(project => project.name),
	datasets: [
		{
			label: 'Horas',
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

const devProjectData = computed(() => ({
	labels: projectList.value.length === 0 ? [] : devList.value.map(dev => dev.name),
	datasets: projectList.value.map((project, i) => ({
		label: project.name,
		data: devList.value.map((dev) => {
			const devHour = project.dev_hours.find(d => d.dev_id === dev.id)
			return devHour?.hours ?? 0
		}),
		backgroundColor: chartColors[i]
	}))
}))

const populateDevList = () => {
	devList.value = []
	for (const project of projectList.value) {
		for (const devHour of project.dev_hours) {
			const dev = devList.value.find(d => d.id === devHour.dev_id)
			if(dev) continue
			devList.value.push({
				id: devHour.dev_id,
				name:  devHour.name
			})
		}
	}
}

onMounted(async () => {
	const overview = await projectsApi.overview()
	projectList.value = overview.projects
	issuesList.value = overview.issues_per_month
	devList.value = projectList.value.map
	populateDevList()
})

</script>
