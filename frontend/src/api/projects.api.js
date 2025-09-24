import api from './config.js'

export default {
	overview: async () => {
		const response = await api.get('/api/projects/overview')
		return response.data
	}
}