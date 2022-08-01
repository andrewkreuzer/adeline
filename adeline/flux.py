from aiohttp import web


async def flux(req: web.Request):
    try:
        scheme, token = req.headers["Authorization"].strip().split(" ")
    except KeyError:
        raise web.HTTPUnauthorized(
            reason="Missing authorization header",
        )
    except ValueError:
        raise web.HTTPForbidden(
            reason="Invalid authorization header",
        )

    if "basic" != scheme.lower():
        raise web.HTTPForbidden(reason="Invalid token scheme")

    if await check_token(token):
        data = await req.json()
        await req.app["db"].insert(data)
        return web.Response(status=200, text="Success")
    else:
        raise web.HTTPForbidden(reason="Token doesn't exist")


async def check_token(token: str) -> bool:
    if token == "mysupersecrettoken":
        return True

    return False
