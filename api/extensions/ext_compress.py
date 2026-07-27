from configs import orqivium_config
from orqivium_app import OrqiviumApp


def is_enabled() -> bool:
    return orqivium_config.API_COMPRESSION_ENABLED


def init_app(app: OrqiviumApp):
    from flask_compress import Compress

    compress = Compress()
    compress.init_app(app)
