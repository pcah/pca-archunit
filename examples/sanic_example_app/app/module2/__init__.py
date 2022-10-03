from sanic import Blueprint
from sanic.response import json

blueprint2 = Blueprint("bp_example2", url_prefix="/my_blueprint2")


@blueprint2.route("/foo")
async def foo2(request):
    return json({"msg": "hi from blueprint2"})
