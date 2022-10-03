#!/usr/bin/env python
from sanic import (
    Blueprint,
    Sanic,
)

from .module1.views import blueprint1
from .module2 import blueprint2
from .module3 import blueprint3

app = Sanic("sanic-example")
blueprint_group = Blueprint.group(blueprint1, blueprint2, url_prefix="/api")

app.blueprint(blueprint_group)
app.blueprint(blueprint3)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999, debug=True)
