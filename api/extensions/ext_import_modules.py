from orqivium_app import OrqiviumApp


def init_app(app: OrqiviumApp):
    from events import event_handlers  # noqa: F401
