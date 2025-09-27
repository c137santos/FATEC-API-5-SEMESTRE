import api from './config.js'

export default {
	overview: async () => {
		const response = await api.get(`/api/core/projects/overview?issues_breakdown_months=${6}`)
		return response.data
	},
	dashboard: async (i) => {
		const response = await api.get(`/api/projects/${i}?issues_breakdown_months=${6}&burdown_days=${30}`)
		return response.data
	}
}