

import DefaultLayout from "@/layouts/default/DefaultLayout.vue"
import OverviewView from "@/pages/core/OverviewView"
import UsersView from "@/pages/accounts/UsersView.vue"

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
        path: "user",
        name: "user",
        component: UsersView,
      },
    ],
  }
]
