import os
import config

def set_config_variables():
	os.environ["SQL_HOST"] = config.SQL_HOST
	os.environ["SQL_USER"] = config.SQL_USER
	os.environ["SQL_PASSWORD"] = config.SQL_PASSWORD
	os.environ["SQL_DATABASE"] = config.SQL_DATABASE

if __name__ == '__main__':
	set_config_variables()
	print(os.environ["SQL_HOST"])
	print(os.environ.get("HELLO", 41))
