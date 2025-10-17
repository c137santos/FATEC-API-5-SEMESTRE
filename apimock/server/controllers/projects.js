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
	},
	developers: (req, res) => {
		const projectId = req.params.id

		const developers = [
			{
				id: 1,
				nome: "Marília Moraes",
				horasTrabalhadas: 159,
				valorHora: 6
			},
			{
				id: 2,
				nome: "Matheus Marciano",
				horasTrabalhadas: 237,
				valorHora: 9
			},
			{
				id: 3,
				nome: "Clara Santos",
				horasTrabalhadas: 262,
				valorHora: 16
			},
			{
				id: 4,
				nome: "Cupcake",
				horasTrabalhadas: 159,
				valorHora: 3.7
			},
			{
				id: 5,
				nome: "Gingerbread",
				horasTrabalhadas: 237,
				valorHora: 16
			}
		]

		res.status(200).send(developers).end()
	}
}
