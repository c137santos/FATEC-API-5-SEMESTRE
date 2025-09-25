

import DefaultLayout from "@/layouts/default/DefaultLayout.vue"
import ProjectDashboardView from "@/pages/core/ProjectDashboardView"
import OverviewView from "@/pages/core/OverviewView"

export default [
	{
		path: "/projects",
		component: DefaultLayout,
		children: [
			{
				path: "overview",
				name: "overview",
				component: OverviewView,
			},
			{
				path: ':id',
				name: 'dashboard',
				component: ProjectDashboardView,
			}
		],
	}
]
