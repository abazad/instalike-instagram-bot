import time
from random import randint

class InstaFollow:
	def __init__(self, operation, repository, content_manager):
		self.operation = operation
		self.user_repository = repository
		self.content_manager = content_manager

		# configuration
		self.max_follows_per_hour = 10
		self.max_unfollows_per_hour = 10

		# users
		self.users = []

		# instance stats
		self.follows = 0
		self.failed_follows = 0
		self.hourly_follows = 0

		# timing
		self.next_follow_time = 0
		self.follow_time_delta = 60 * 60 // ((self.max_follows_per_hour + self.max_unfollows_per_hour) // 2)

		self.t0 = time.time()
		self.t1 = 0

	def follow(self, user_id):
		response = self.operation.follow(user_id)

		if (response.status_code != 200):
			self.failed_follow()
			return False

		self.followed_successfully(user_id)
		return True

	def act(self):
		if (len(self.users) == 0):
			# users may be duplicated
			self.users = self.content_manager.get_users()
		if (time.time() < self.next_follow_time):
			return

		user = self.users.pop()
		if (not self.follow(user)):
			self.users.insert(0, user)

		self.update_timer(self.follow_time_delta - (self.follow_time_delta // 2), self.follow_time_delta + (self.follow_time_delta // 2))

	def update_timer(self, mini, maxi):
		self.next_follow_time = time.time() + randint(mini, maxi)
		self.get_stats()

	def failed_follow(self):
		self.failed_follows += 1

	def followed_successfully(self, user_id):
		# self.user_repository.follow(self, user_id)
		self.follows += 1
		self.hourly_follows += 1

	def get_stats(self):
		self.t1 = time.time()
		per_hour = ((self.follows + self.failed_follows) * 60 * 60) // (1 if (self.t1 - self.t0) == 0 else self.t1 - self.t0)
		self.log('#######################################')
		self.log('---------------FOLLOWS-----------------')
		self.log('total time: {0:.0f}s'.format(self.t1 - self.t0))
		self.log('follows: {0}'.format(self.follows))
		self.log('failed follows: {0}'.format(self.failed_follows))
		self.log('estimated follows per hour: {0:.0f}'.format(per_hour))
		self.log('next follow in: {0:.0f}s'.format(self.next_follow_time - time.time()))
		self.log('users to follow: {0}'.format(len(self.users)))

	def log(self, text):
		print(text)
		