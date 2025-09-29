

import DefaultLayout from "@/layouts/default/DefaultLayout.vue"
import IssuesView from "@/pages/core/IssuesView"
import OverviewView from "@/pages/core/OverviewView"
import UserView from "@/pages/core/UserView"

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
        component: IssuesView,
      },
      {
        path: "user",
        name: "user",
        component: UserView,
      }
    ],
  }
]
