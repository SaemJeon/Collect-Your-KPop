import sqlite3, os, csv
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
		user_id = self.select('SELECT last_insert_rowid();')
		self.create_user_album_data(user_id[0][0])
		self.create_user_photo_data(user_id[0][0])
	
	def create_user_album_data(self, user_id):
		with open('../code/db/albums.csv') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				self.execute('INSERT INTO user_albums (user_id, group_id, album_id, name, collected) VALUES (?, ?, ?, ?, ?)',
				[user_id, int(row[0]), int(row[1]), row[2], int(row[3])])
		return

	def create_user_photo_data(self, user_id):
		with open('../code/db/photocards.csv') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				self.execute('INSERT INTO user_photos (user_id, group_id, member_id, photo_id, collected) VALUES (?, ?, ?, ?, ?)',
				[user_id, int(row[0]), int(row[1]), row[2], int(row[3])])
		return

	def update_profile(self, artist, member, city, state, zipcode, distance, language, user_id):
		self.execute('UPDATE users SET artist=?, member=?, city=?, state=?, zipcode=?, distance=?, language=? WHERE user_id=?',
		[artist, member, city, state, zipcode, distance, language, user_id])

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
				'city': d[7],
				'state': d[8],
				'zipcode': d[9],
				'distance': d[10],
				'language': d[11]
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

	# Return favorite artist and member of user
	def get_my_pop(self, user_id):
		data = self.select('SELECT * FROM users where user_id=?', [user_id])
		if data:
			d = data[0]
			artist = self.select('SELECT name from groups where group_id=?', [d[5]])
			member = self.select('SELECT name from members where member_id=?', [d[6]])
			if d[11] == "EN":
				lang = "English"
			elif d[11] == "KR":
				lang = "Korean"
			else:
				lang = "None"

			return {
				'artist': artist,
				'member': member,
				'city': d[7],
				'state': d[8],
				'zipcode': d[9],
				'distance': d[10],
				'language': lang
			}
		else:
			return None
	
	def updateAlbum(self, user_id, group_id, album_id):
		self.execute('UPDATE user_albums SET collected=not collected WHERE user_id=? and group_id=? and album_id=?', 
		[user_id, group_id, album_id])
	
	def getAlbums(self, user_id, group_id):
		data = self.select('SELECT * from user_albums WHERE user_id=? and group_id=?', [user_id, group_id])
		if data:
			albums = {}
			for i in range(len(data)):
				albums[i+1] = data[i]
			return albums
		else:
			return None

	def getPhotos(self, user_id, group_id, member_id):
		data = self.select('SELECT * from user_photos WHERE user_id=? and group_id=? and member_id=?', [user_id, group_id, member_id])
		if data:
			photos = {}
			for i in range(len(data)):
				photos[i+1] = data[i]
			return photos
		else:
			return None
	
	def updatePhoto(self, user_id, group_id, member_id, photo_id):
		self.execute('UPDATE user_photos SET collected=not collected WHERE user_id=? and group_id=? and member_id=? and photo_id=?', 
		[user_id, group_id, member_id, photo_id])
	
	def addProduct(self, user_id, group_id, sell_type, album_id, member_id, delivery, zipcode, distance, fee, price, sold, confirm):
		self.execute('INSERT INTO products (user_id, group_id, sell_type, album_id, member_id, delivery, zipcode, distance, shipping_fee, price, sold, confirm) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
		[user_id, group_id, sell_type, album_id, member_id, delivery, zipcode, distance, fee, price, sold, confirm])

	def getProducts(self):
		data = self.select('SELECT * from products WHERE sold=0')
		if data:
			products = {}
			for i in range(len(data)):
				products[i+1] = list(data[i])
			return products
		else:
			return None
		
	def applyFilter(self, group_id, sell_type, album_id, member_id, price, delivery):
		data = None
		sql = "SELECT * FROM products WHERE " + " AND ".join([
			self.constructCondition("group_id", group_id), 
			self.constructCondition("sell_type", sell_type), 
			self.constructCondition("album_id", album_id),
			self.constructCondition("member_id", member_id),
			self.constructCondition("delivery", delivery),
			self.constructCondition("sold", 0)])
		if price == "1":
			sql += " ORDER BY price ASC"
		elif price == "2":
			sql += " ORDER BY price DESC"
		
		data = self.select(sql)

		if data:
			products = {}
			for i in range(len(data)):
				products[i+1] = list(data[i])
			return products
		else:
			return None
		return

	def constructCondition(self, field_name, field_value):
		return field_name + " = " + str(field_value) if field_value else "(" + field_name + " is null or " + field_name + " like '%')"
	
	def addToCart(self, user_id, product_id):
		seller_id = self.select('SELECT user_id FROM products WHERE product_id=?', [product_id])
		if str(user_id) != str(seller_id[0][0]):
			data = self.select('SELECT * FROM cart WHERE user_id=? and product_id = ?', [user_id, product_id])
			if not data:
				self.execute('INSERT INTO cart (user_id, product_id) VALUES (?, ?)', [user_id, product_id])
				return "Added"
		return "It is on your selling list."
	
	def getShoppingCart(self, user_id):
		data = self.select("SELECT * FROM products WHERE product_id IN (SELECT product_id FROM cart WHERE user_id=?) and sold=0", [user_id])
		if data:
			products = {}
			for i in range(len(data)):
				products[i+1] = list(data[i])
			return products
		else:
			return None
		return
	
	def getMySelling(self, user_id):
		data = self.select("SELECT * FROM products WHERE user_id=?", [user_id])
		if data:
			products = {}
			for i in range(len(data)):
				products[i+1] = list(data[i])
			return products
		else:
			return None
		return
	
	def removeFromCart(self, user_id, product_id):
		self.execute('DELETE FROM cart WHERE user_id=? and product_id=?', [user_id, product_id])
	
	def buyProduct(self, user_id, product_id):
		self.execute('UPDATE products SET sold=1 WHERE product_id=?', [product_id])
		data = self.select('SELECT * FROM orders WHERE user_id=? and product_id = ?', [user_id, product_id])
		if not data:
			self.execute('INSERT INTO orders (user_id, product_id, confirm) VALUES(?, ?, ?)', [user_id, product_id, 0])
		self.removeFromCart(user_id, product_id)
	
	def getOrderHistory(self, user_id):
		data = self.select("SELECT * FROM products WHERE product_id IN (SELECT product_id FROM orders WHERE user_id=?)", [user_id])
		if data:
			products = {}
			for i in range(len(data)):
				products[i+1] = list(data[i])
			return products
		else:
			return None
		return

	def confirmOrder(self, user_id, product_id):
		self.execute('UPDATE products SET confirm=1 WHERE product_id=?', [product_id])
		self.execute('UPDATE orders SET confirm=1 WHERE user_id=? and product_id=?', [user_id, product_id])

	def close(self):
		self.conn.close()
