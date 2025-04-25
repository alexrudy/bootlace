from flask import Flask

from bootlace.extension import Bootlace

app = Flask(__name__)
bootlace = Bootlace(app)
