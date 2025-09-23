const data = require('../data')

module.exports = {
	overview: (req, res) => {
		res.status(200).send(data.projectsOverview).end()
	}
}