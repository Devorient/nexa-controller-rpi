from flask import Flask
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')

from nexa_controller_rpi import switcher

from app import views