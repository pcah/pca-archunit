from sanic import (
    Sanic,
    response,
)

links = [("handler_text", "info"), ("feed", "newsfeed")]


def add_routes(app: Sanic) -> None:
    app.add_route(handler_text, "/text")
    app.add_websocket_route(feed, "/feed")


def handler_text(request):
    return response.text("Hello!")


async def feed(request, ws):
    while True:
        data = "hello!"
        print("Sending: " + data)
        await ws.send(data)
        data = await ws.recv()
        print("Received: " + data)
