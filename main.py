import os
import config
from app import app


def set_config_variables():
	os.environ["SQL_HOST"] = config.SQL_HOST
	os.environ["SQL_USER"] = config.SQL_USER
	os.environ["SQL_PASSWORD"] = config.SQL_PASSWORD
	os.environ["SQL_DATABASE"] = config.SQL_DATABASE


if __name__ == '__main__':
	set_config_variables()
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)
