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

const initiateDataset = () => {
	const datasets = []
	let i = 0
	for (const issue of issuesList.value) {
		for (const key of Object.keys(issue)) {
			if(key === 'date') continue
			const dataset = datasets.find(d => d.label === key)
			if (dataset) continue
			datasets.push({ 
				label: key,
				data: [],
				backgroundColor: chartColors[i],
				borderColor: chartColors[i] 
			})
			i ++
		}
	}
	return datasets
}

const populateDataset = (datasets) => {
	for (const issue of issuesList.value) {
		for (const [key, value] of Object.entries(issue)) {
			if(key === 'date') continue
			const dataset = datasets.find(d => d.label === key)
			dataset.data.push(value)
		}
	}
}

const statusBreakdownData = computed(() => {
	const datasets = initiateDataset()
	populateDataset(datasets)
	
	return {
		labels: issuesList.value.map(issue => issue.date),
		datasets,
	} 
})

</script>