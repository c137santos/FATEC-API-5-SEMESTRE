<template>
	<v-sheet 
		class="mx-auto my-8 bg-transparent"
		max-width="1400"
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
		 </v-row>
		 <v-row>
		 </v-row>
		 <div :key="projectList.map(p => p.id).join()">
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
					<Line
						:data="statusBreakdownData"
						:options="{
							responsive: true,
							plugins: {
								legend: {
									position: 'top'
								}
							}
						}"
					>
					</Line>
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
		 </div>
		</v-container>
	</v-sheet>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import projectsApi from '@/api/projects.api'
import { chartColors } from '@/utils/chart-utils'

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

const statusBreakdownData = computed(() => ({
	labels: issuesList.value.map(issue => issue.date),
	datasets: [
		{
			label: "Pendente",
			data: issuesList.value.map(issue => issue.pending),
			backgroundColor: chartColors[0],
			borderColor: chartColors[0]
		},
		{
			label: "Em andamento",
			data: issuesList.value.map(issue => issue.on_going),
			backgroundColor: chartColors[1],
			borderColor: chartColors[1]
		},
		{
			label: "MR",
			data: issuesList.value.map(issue => issue.mr),
			backgroundColor: chartColors[2],
			borderColor: chartColors[2]
		},
		{
			label: "Concluido",
			data: issuesList.value.map(issue => issue.concluded),
			backgroundColor: chartColors[3],
			borderColor: chartColors[3]
		},
		
	]
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