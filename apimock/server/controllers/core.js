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

    const mappedIssues = data.issues.map(issue => ({
      jira_id: issue.key,
      description: issue.fields.summary,
      created_at: issue.fields.created,
      user_related: {
        user_name: issue.fields.assignee.displayName
      }
    }));

    const response = {
      issues: mappedIssues,
      total_items: mappedIssues.length
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
