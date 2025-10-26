import api from './config.js'

export default {
	overview: async () => {
		const response = await api.get(`/api/core/projects/overview?issues_breakdown_months=${6}`)
		return response.data
	},
	dashboard: async (i) => {
		const response = await api.get(`/api/core/projects/${i}?issues_breakdown_months=${6}&burdown_days=${30}`)
		return response.data
	},
	getDevelopers: async (projectId) => {
		const response = await api.get(`/api/core/projects/${projectId}/desenvolvedores`)
		const developers = response.data || []

		const totalWorkedHours = developers.reduce((acc, dev) => acc + (dev.horasTrabalhadas || 0), 0)

		let hourValue = 0
		if (totalWorkedHours > 0) {
			hourValue = developers.reduce((acc, dev) => acc + ((dev.horasTrabalhadas || 0) * (dev.valorHora || 0)), 0) / totalWorkedHours
		}

		return {
			developers,
			total_worked_hours: totalWorkedHours,
			hourValue,
		}
	},
	updateDeveloperHourValue: async (projectId, userId, valorHora) => {
		const response = await api.patch(`/api/core/projects/${projectId}/desenvolvedores/${userId}`, {
			valorHora
		})
		return response.data
	}
}
