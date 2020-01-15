from flask import Flask
from app.helpers import verify_password
application = Flask(__name__, instance_relative_config=True)
application.config.from_object('config')
application.config.from_object('config_local')

from nexa_controller_rpi import switcher

from application import views