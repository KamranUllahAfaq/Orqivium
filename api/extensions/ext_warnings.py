from orqivium_app import OrqiviumApp


def init_app(app: OrqiviumApp):
    import warnings

    warnings.simplefilter("ignore", ResourceWarning)
