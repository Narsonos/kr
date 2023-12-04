from locust import HttpUser, task
from random import choice

userlist = [(f'user{i}',f'password{i}') for i in range(100)]

class User(HttpUser):
	host = "http://192.168.88.248:5000"
	@task
	def load_login(self):
		self.client.get("/login")
		
	#@task
	def validation(self):
		username,password = choice(userlist)
		response = self.client.post("/login_validate", {'username':username, 'password':password, 'actual_login':'no'})

	#@task
	def graph(self):
		response = self.client.post("/login_validate", {'username':'user1', 'password':'password1', 'actual_login':'yes'})

