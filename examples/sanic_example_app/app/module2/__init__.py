from sanic import Blueprint
from sanic.response import json

blueprint2 = Blueprint("blueprint-module-2", url_prefix="/my_blueprint2")


links = [("blueprint-module-2.foo2", "foo-details")]


@blueprint2.route("/foo")
async def foo2(request):
    return json({"msg": "hi from blueprint2"})
