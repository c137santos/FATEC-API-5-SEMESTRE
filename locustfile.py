from locust import HttpUser, task

class JiboiaUser(HttpUser):
	@task
	def base_test(self):
		self.client.get('/api/core/issues/list')
		self.client.get('/api/core/projects/overview?issues_breakdown_months=6')
		self.client.get('/api/core/projects/1?issues_breakdown_months=6&burdown_days=30')