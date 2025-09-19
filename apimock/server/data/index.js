const utils = require('../utils')

module.exports = {
  users: utils.parseJson('./data/users.json'),
  issues: utils.parseJson('./data/issues.json'),
}
