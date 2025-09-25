<template>
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
</template>

<script setup>
import { Line } from 'vue-chartjs'
import { defineModel, computed } from 'vue'
import { chartColors } from '@/utils/chart-utils'

const issuesList = defineModel()

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
</script>