// Composables
import EmptyLayout from "@/layouts/default/EmptyLayout.vue"
import LoginView from "@/pages/accounts/LoginView.vue"
import LogoutView from "@/pages/accounts/LogoutView.vue"
import UsersView from "@/pages/accounts/UsersView.vue"

export default [
  {
    path: "/accounts",
    component: EmptyLayout,
    children: [
      {
        path: "login",
        name: "accounts-login",
        component: LoginView,
      },
      {
        path: "logout",
        name: "accounts-logout",
        component: LogoutView,
      },
      {
        path: "users",
        name: "accounts-users",
        component: UsersView,
      },
    ],
  },
]
