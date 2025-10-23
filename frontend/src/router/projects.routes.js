

import DefaultLayout from "@/layouts/default/DefaultLayout.vue"
import ProjectDashboardView from "@/pages/core/ProjectDashboardView"
import OverviewView from "@/pages/core/OverviewView"
import IssueListView from "@/pages/core/IssueListView.vue"

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
			},
			{
				path: ':id/issues',
				name: 'project-issues',
				component: IssueListView,
			},
		],
	},
]
