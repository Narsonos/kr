from kr import app
from kr import db

if __name__ == "__main__":
	db.init_app(app)
	app.run()
