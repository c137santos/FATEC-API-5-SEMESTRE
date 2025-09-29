<template>
	<DashboardLayout>
		<template #title> Project Dashboard: {{ name }} </template>
    <v-container>
			<v-row>
				<v-col>
					<v-text-field
						v-model.number="hourValue"
						style="max-width: 10rem;"
						label="Valor Hora"
						type="number"
					></v-text-field>
				</v-col>
			</v-row>
			<v-row>
				<v-col>
					<span class="w-100 d-flex justify-center"> Movimentação de issues (por mês) </span>
					<StatusBreakdownGraph v-model="issuesList"></StatusBreakdownGraph>
				</v-col>
				<v-col>
					<span class="w-100 d-flex justify-center">Burndown</span>
					<Line :data="burndownData"></Line>
				</v-col>
			</v-row>
			<v-row>
				<v-col>
					<div class="h-100 d-flex flex-column ga-4">
							<span class="w-100 d-flex justify-center">Status das Issues</span>
							<div class="flex-grow-1">
								<Doughnut
									:data="issueStatusData"
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
				<v-col>
					<div class="d-flex flex-column ga-4">
						<v-card class="d-flex flex-column ga-2 pa-4">
							<h3 class="d-flex justify-center">Total Horas</h3>
							<span class="text-h4 d-flex justify-center">{{ workedHours }}</span>
						</v-card>
						<v-card class="d-flex flex-column ga-2 pa-4">
							<h3 class="d-flex justify-center">Gasto por hora (R$)</h3>
							<span class="text-h4 d-flex justify-center">{{ workedHours * hourValue }}</span>
						</v-card>
					</div>
				</v-col>
				<v-col>
					<div class="h-100 d-flex flex-column ga-4">
							<span class="w-100 d-flex justify-center">Tipos de Issues</span>
							<div class="flex-grow-1">
								<Doughnut
									:data="issuesTypeData"
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
			<v-row>
				<v-col>
					<v-card class="d-flex flex-column ga-2 pa-4">
						<h3 class="d-flex justify-center">Total de Issues</h3>
						<span class="text-h4 d-flex justify-center">{{ issuesTotal }}</span>
					</v-card>
				</v-col>
				<v-col>
					<v-card class="d-flex flex-column ga-2 pa-4">
						<h3 class="d-flex justify-center">Horas trabalhadas</h3>
						<span class="text-h4 d-flex justify-center">{{ workedHours }}</span>
					</v-card>
				</v-col>
				<v-col>
					<v-card class="d-flex flex-column ga-2 pa-4">
						<h3 class="d-flex justify-center">Issues Ativas</h3>
						<span class="text-h4 d-flex justify-center">{{ activeIssues }}</span>
					</v-card>
				</v-col>
				<v-col>
					<v-card class="d-flex flex-column ga-2 pa-4">
						<h3 class="d-flex justify-center">Issues Concluidas</h3>
						<span class="text-h4 d-flex justify-center">{{ concludedIssues }}</span>
					</v-card>
				</v-col>
			</v-row>
			<v-row justify="center">
				<v-col>
					<div style="height: 248px">
						<Bar
							:data="devHoursData"
							:options="{
								responsive: true,
								aspectRatio: false,
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
			</v-row>
		</v-container>

	</DashboardLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { dateDiffInDays, toISODate } from '@/utils/date-formulas';
import projectsApi from '@/api/projects.api';
import { Line, Doughnut, Bar } from 'vue-chartjs'
import DashboardLayout from '@/layouts/default/DashboardLayout.vue';
import StatusBreakdownGraph from '@/components/StatusBreakdownGraph.vue'
import { chartColors } from '@/utils/chart-utils';
import { useRoute } from 'vue-router';

const route = useRoute()

const issuesList = ref([])
const dataRef = ref()
const name = ref('')

const hourValue = ref(0)

const emptyDataset = {
	labels: [],
	datasets: [],
}

const burndownData = computed(() => {
	const burndown = dataRef.value?.burndown
	if (!burndown) return emptyDataset

	const daysRange = dateDiffInDays(toISODate(burndown.end_date), toISODate(burndown.pending_per_day[0].date))

	const endDateTimestamp = new Date(toISODate(burndown.end_date)).getTime()
	const formatter = new Intl.DateTimeFormat('pt-BR', {
		year: 'numeric',
		month: '2-digit',
		day: '2-digit',
	})

	const daysLabelList = []

	for(let i = 0; i < daysRange; i ++) {
		const date = new Date(endDateTimestamp - (i * 24 * 360 * 10000))
		const dateString = formatter.format(date)
		daysLabelList.unshift(dateString)
	}

	const burndownMax = burndown.pending_per_day[0].pending
	const step = burndownMax / daysLabelList.length

	return {	
		labels: [...daysLabelList, ''],
		datasets: [
			{
				label: 'Burndown',
				data: [...daysLabelList.map((_, i) => burndownMax - (step * i)), 0],
				borderColor: chartColors[1]
			},
			{
				label: 'Pedencias',
				data: burndown.pending_per_day.map(p => p.pending),
				borderColor: chartColors[2]
			}
		],
	}
})

const issueStatusData = computed(() => {
	const issuesStatus = dataRef.value?.issues_today

	if(!issuesStatus) return emptyDataset
	delete issuesStatus.date

	return {
		labels: Object.keys(issuesStatus),
		datasets: [
			{
				data: Object.values(issuesStatus),
				backgroundColor: chartColors,
				borderColor: 'rgba(0,0,0,0)'
			},
		]
	}
})

const issuesTypeData = computed(() => {
	const issuesType = dataRef.value?.issues_status
	if(!issuesType) return emptyDataset

	return {
		labels: Object.keys(issuesType),
		datasets: [
			{
				data: Object.values(issuesType),
				borderColor: 'rgba(0, 0, 0, 0)',
				backgroundColor: chartColors,
			}
		]
	}
})

const devHoursData = computed(() => {
	const devData = dataRef.value?.dev_hours

	if(!devData) return emptyDataset
	return {
		labels: devData.map(d => d.name),
		datasets: [
			{
				label: 'Horas trabalhadas',
				data: devData.map(d => d.hours),
				backgroundColor: chartColors[6],
			},
		]
}
})

const workedHours = computed(() => !dataRef.value ? 0 : dataRef.value.total_worked_hours)

const activeIssues = computed(() => !dataRef.value ? 0 : (() => {
	const today = dataRef.value.issues_today
	return Object.values(today).reduce((total, value) => total + value, 0) - today['Concluído']
})())
const concludedIssues = computed(() => !dataRef.value ? 0 : dataRef.value.issues_today['Concluído'])

const issuesTotal = computed(() => !dataRef.value ? 0 : (() => {
	const today = dataRef.value.issues_today
	return Object.values(today).reduce((total, value) => total + value, 0)
})())

onMounted(async () => {
	const data = await projectsApi.dashboard(route.params.id)
	name.value = data.name
	dataRef.value = data
	issuesList.value = data.issues_per_month
})

</script>
