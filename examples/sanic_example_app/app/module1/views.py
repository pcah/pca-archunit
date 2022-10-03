from sanic import Blueprint
from sanic.response import json

blueprint1 = Blueprint("blueprint-module-1", url_prefix="/bp1")


@blueprint1.route("/foo")
async def foo(request):
    return json({"msg": "hi from blueprint"})
