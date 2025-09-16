<template>
	<v-sheet 
		class="mx-auto mt-12"
		max-width="800"
		elevation="8"
	>
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
							<v-slide-group-item v-for="(name, i) in projectList" :key="i" v-slot="{ isSelected, toggle }">
								<v-btn
									:color="isSelected ? 'primary' : undefined"
									class="ma-2"
									@click="toggle"
								> {{ name }} </v-btn>
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
		 <v-row>
			<v-col>
				<span class="w-100 d-flex justify-center">Horas por projeto</span>
				<Bar
					:data="data"
					:options="{
						responsive: true,
						indexAxis: 'y',
					}"
				></Bar>
			</v-col>
			<v-col>
				<span class="w-100 d-flex justify-center">Issues por projeto</span>
				<Doughnut :data="donutData"></Doughnut>
			</v-col>
		 </v-row>
		</v-container>
	</v-sheet>
</template>

<script lang="ts" setup>
import { Bar, Doughnut } from 'vue-chartjs'

const projectList = [
	'Project 1',
	'Project 2',
	'Project 3',
	'Project 4',
	'Project 5',
]

const data = {
	labels: projectList,
	datasets: [
		{
			label: 'Horas',
			data: [1, 2, 3, 4, 5],
			borderColor: '#42A5F5',
			backgroundColor: '#1565C0'

		}
	]
}
const donutData = {
	labels: projectList,
	datasets: [
		{
			label: 'Issues',
			backgroundColor: ['#EC407A', '#AB47BC', '#5C6BC0', '#26C6DA', '#26A69A'],
			borderColor: 'rgba(0, 0, 0, 0)',
			data: [2, 5, 3, 1, 5]
		}
	]
}
</script>