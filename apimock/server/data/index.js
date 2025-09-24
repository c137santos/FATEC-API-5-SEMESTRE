const utils = require('../utils')

module.exports = {
  users: utils.parseJson('./data/users.json'),
  projectsOverview: utils.parseJson('./data/projects/overview.json')
}
