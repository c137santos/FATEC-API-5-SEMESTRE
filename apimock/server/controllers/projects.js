const data = require('../data')

module.exports = {
	list: (req, res) => {
		res.status(200).send(data.projects).end()
	}
}