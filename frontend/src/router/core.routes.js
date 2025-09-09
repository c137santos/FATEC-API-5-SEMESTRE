// Composables
import DefaultLayout from "@/layouts/default/DefaultLayout.vue"
import CardListView from "@/pages/core/CardListView.vue"

export default [
  {
    path: "/cards",
    component: DefaultLayout,
    children: [
      {
        path: "list",
        name: "cards-list",
        component: CardListView,
      },
    ],
  },
]
