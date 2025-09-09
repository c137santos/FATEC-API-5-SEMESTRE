const data = require("../data");
const accounts = require("./accounts");

function getMaxId(items) {
  return Math.max(...items.map((item) => item.id));
}

module.exports = {
  find: (req, res) => {
    const loggedUser = accounts.loginRequired(req, res);
    if (!loggedUser) {
      return;
    }
    const { id } = req.params;
    if (id != undefined) {
      const card = data.cards.find((t) => t.id == id);
      if (!card || card.userId != loggedUser.id) {
        res.status(404).end();
        return;
      }
      res.send(card);
      return;
    }
    const response = {
      cards: data.cards.filter((t) => t.userId == loggedUser.id),
    };
    res.send(response);
  },
  add: (req, res) => {
    const loggedUser = accounts.loginRequired(req, res);
    if (!loggedUser) {
      return;
    }
    const { description } = req.body;
    const id = getMaxId(data.cards) + 1;
    const newCard = {
      id,
      description,
      userId: loggedUser.id,
    };
    data.cards.push(newCard);
    res.send(newCard);
  },
};
