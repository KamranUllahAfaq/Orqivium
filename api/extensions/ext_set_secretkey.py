from configs import orqivium_config
from configs.secret_key import resolve_secret_key
from orqivium_app import OrqiviumApp


def init_app(app: OrqiviumApp) -> None:
    """Resolve SECRET_KEY after config loading and before session/login setup."""
    secret_key = orqivium_config.SECRET_KEY
    if not secret_key:
        secret_key = resolve_secret_key(secret_key)
    orqivium_config.SECRET_KEY = secret_key
    app.config["SECRET_KEY"] = secret_key
    app.secret_key = secret_key
