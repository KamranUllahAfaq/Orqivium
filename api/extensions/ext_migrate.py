from orqivium_app import OrqiviumApp


def init_app(app: OrqiviumApp):
    import flask_migrate

    from extensions.ext_database import db

    flask_migrate.Migrate(app, db)
