const data = require("../data");
function getMaxId(items) {
  return Math.max(...items.map((item) => item.id));
}

module.exports = {
  find: (req, res) => {
    const mappedIssues = data.issues.map(issue => ({
      jira_id: issue.key,
      description: issue.fields.summary,
      details: issue.fields.details,
      created_at: issue.fields.created,
      user_related: {
        user_name: issue.fields.assignee.displayName
      },
      time_spend_hours: issue.fields.timespent / 3600,
    }));

    const response = {
      issues: mappedIssues,
      total_items: mappedIssues.length
    };

    res.send(response);
  },
};
