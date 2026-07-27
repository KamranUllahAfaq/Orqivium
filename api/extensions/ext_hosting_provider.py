from core.hosting_configuration import HostingConfiguration

hosting_configuration = HostingConfiguration()


from orqivium_app import OrqiviumApp


def init_app(app: OrqiviumApp):
    hosting_configuration.init_app(app)
