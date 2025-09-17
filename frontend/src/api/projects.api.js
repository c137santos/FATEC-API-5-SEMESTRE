import api from './config.js'

export default {
	list: async () => {
		const response = await api.get('/api/projects/list')
		return response.data
	}
}