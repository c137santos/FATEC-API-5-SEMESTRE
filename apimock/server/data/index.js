const utils = require('../utils')

module.exports = {
  users: utils.parseJson('./data/users.json'),
  cards: utils.parseJson('./data/cards.json'),
  projectsOverview: utils.parseJson('./data/projects/overview.json')
}
