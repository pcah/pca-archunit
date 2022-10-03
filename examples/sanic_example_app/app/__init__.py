#!/usr/bin/env python
from sanic import (
    Blueprint,
    Sanic,
    response,
)

from . import (
    module2,
    views,
)
from .module1.links import links as module1_links
from .module1.views import blueprint1
from .module3 import blueprint3
from .utils import hateoas_links

app = Sanic("sanic-example")
blueprint_group = Blueprint.group(blueprint1, module2.blueprint2, url_prefix="/api")

views.add_routes(app)
app.blueprint(blueprint_group)
app.blueprint(blueprint3)


@app.route("/")
def index(request):
    links = [("index", "self")] + views.links + module1_links + module2.links
    return response.json({"links": hateoas_links(app, links)})


def start():
    app.run(host="0.0.0.0", port=9999, debug=True)


if __name__ == "__main__":
    start()
