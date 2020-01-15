from flask import Flask
from app.helpers import verify_password
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_object('config_local')

from nexa_controller_rpi import switcher

from app import views