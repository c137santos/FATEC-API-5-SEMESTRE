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
      const issue = data.issues.find((t) => t.id == id);
      if (!issue || issue.userId != loggedUser.id) {
        res.status(404).end();
        return;
      }
      res.send(issue);
      return;
    }
    const response = {
      issues: data.issues.filter((t) => t.userId == loggedUser.id),
    };
    res.send(response);
  },
  add: (req, res) => {
    const loggedUser = accounts.loginRequired(req, res);
    if (!loggedUser) {
      return;
    }
    const { description } = req.body;
    const id = getMaxId(data.issues) + 1;
    const newIssue = {
      id,
      description,
      userId: loggedUser.id,
    };
    data.issues.push(newIssue);
    res.send(newIssue);
  },
};
