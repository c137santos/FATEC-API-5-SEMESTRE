const utils = require('../utils')

module.exports = {
  users: utils.parseJson('./data/users.json'),
  projectsOverview: utils.parseJson('./data/projects/overview.json'),
  projectsDashboard: utils.parseJson('./data/projects/dashboard.json'),
  issues: utils.parseJson('./data/issues.json')
}
