import typing as t


class Sanicable(t.Protocol):
    def url_for(handler_name: str, *args, **kwargs) -> str:
        ...


def hateoas_link(
    app: Sanicable,
    handler_name: str,
    relation: str,
) -> dict:
    return {"rel": [relation], "url": app.url_for(handler_name)}


def hateoas_links(app: Sanicable, params: t.List[dict]) -> t.List[dict]:
    print("!!!", params)
    return [hateoas_link(app, handler_name, relation) for handler_name, relation in params]
