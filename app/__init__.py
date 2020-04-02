from flask import Flask

app = Flask(__name__)

app.debug = True
app.templates_auto_reload = True

from app import routes