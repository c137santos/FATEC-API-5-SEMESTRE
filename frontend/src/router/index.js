import { createRouter, createWebHistory } from "vue-router"
import accountsRoutes from "./accounts.routes"
import baseRoutes from "./base.routes"
import coreRoutes from "./core.routes"
import projectsRoutes from './projects.routes'
import Page404View from "@/pages/base/Page404View.vue"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...baseRoutes,
    ...accountsRoutes,
    ...coreRoutes,
    ...projectsRoutes,
    {
      path: "/:pathMatch(.*)*",
      name: "page-not-found-404",
      component: Page404View,
    },
  ],
})

export default router
