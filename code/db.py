import sqlite3, os
from flask import g

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'kpop.db')


class Database:

	def __init__(self):
		self.conn = sqlite3.connect(DATABASE_PATH)

	def select(self, sql, parameters=[]):
		c = self.conn.cursor()
		c.execute(sql, parameters)
		return c.fetchall()

	def execute(self, sql, parameters=[]):
		c = self.conn.cursor()
		c.execute(sql, parameters)
		self.conn.commit()

	def get_goats(self, n, offset):
		data = self.select(
				'SELECT * FROM goats ORDER BY uid ASC LIMIT ? OFFSET ?', [n, offset])
		return [{
				'uid': d[0],
				'name': d[1],
				'age': d[2],
				'adopted': d[3],
				'image': d[4]
		} for d in data]

	def get_user_goats(self, user_id):
		data = self.select(
				'SELECT * FROM goats WHERE adopted=? ORDER BY uid ASC', [user_id])
		return [{
				'uid': d[0],
				'name': d[1],
				'age': d[2],
				'adopted': d[3],
				'image': d[4]
		} for d in data]

	def get_total_goat_count(self):
		data = self.select('SELECT COUNT(*) FROM goats')
		return data[0][0]

	def update_goat_adopted(self, goat_id, user_id):
		self.execute('UPDATE goats SET adopted=? WHERE uid=?', [user_id, goat_id])

	def create_account(self, name, email, encrypted_password, dob, artist, member):
		self.execute('INSERT INTO users (name, email, encrypted_password, dob, artist, member) VALUES (?, ?, ?, ?, ?, ?)',
		 [name, email, encrypted_password, dob, artist, member])

	# Return User Info
	def get_user(self, email):
		data = self.select('SELECT * FROM users WHERE email=?', [email])
		if data:
			d = data[0]
			return {
				'user_id': d[0],
				'name': d[1],
				'email': d[2],
				'encrypted_password': d[3],
			}
		else:
			return None
	
	# Return user profile info
	def get_profile(self, user_id):
		data = self.select('SELECT * FROM users where user_id=?', [user_id])
		if data:
			d = data[0]
			return {
				'artist': d[5],
				'member': d[6],
				'location': d[7],
				'distance': d[8],
				'phone': d[9],
				'language': d[10]
			}
		else:
			return None

	# Return all groups
	def get_groups(self):
		data = self.select('select * from groups')
		if data:
			groups = {}
			for i in range(len(data)):
				groups[i] = data[i]
			return groups
		else:
			return None
	
	# Return all the members of the group
	def get_members(self, group_id):
		data = self.select('select * from members where group_id=?', [group_id])
		if data:
			members = {}
			for i in range(len(data)):
				members[i] = data[i]
			return members
		else:
			return None

	def close(self):
		self.conn.close()
