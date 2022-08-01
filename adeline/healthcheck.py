from aiohttp import web

async def healthcheck(req: web.Request):
    smc = req.app['socket_mode_client']
    if (
        smc is not None
        and await smc.is_connected()
    ):
        return web.Response(status=200, text="OK")
    return web.Response(status=503, text="The Socket Mode client is inactive")


