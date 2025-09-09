const utils = require('../utils')

module.exports = {
  users: utils.parseJson('./data/users.json'),
  cards: utils.parseJson('./data/cards.json'),
}
