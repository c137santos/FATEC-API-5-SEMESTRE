

import DefaultLayout from "@/layouts/default/DefaultLayout.vue"
import OverviewView from "@/pages/core/OverviewView"
import UserView from "@/pages/core/UserView"
import IssueListView from "@/pages/core/IssueListView.vue"

export default [
  {
    path: "/",
    component: DefaultLayout,
    children: [
      {
        path: "overview",
        name: "overview",
        component: OverviewView,
      },
      {
        path: "issues",
        name: "issues",
        component: IssueListView,
      },
      {
        path: "user",
        name: "user",
        component: UserView,
      },
    ],
  }
]
