from configs import orqivium_config
from orqivium_app import OrqiviumApp


def init_app(app: OrqiviumApp):
    if orqivium_config.RESPECT_XFORWARD_HEADERS_ENABLED:
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app, x_port=1)  # type: ignore[method-assign]
