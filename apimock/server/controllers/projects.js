const data = require('../data')

module.exports = {
	overview: (req, res) => {
		res.status(200).send(data.projectsOverview).end()
	},
	byProject: (req, res) => {
		const projectId = req.params.id
		const project = data.projectsDashboard.find((p) => {
			return p.project_id == projectId
		})

		res.status(200).send(project).end()
	}
}
