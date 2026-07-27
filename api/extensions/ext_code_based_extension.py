from core.extension.extension import Extension
from orqivium_app import OrqiviumApp


def init_app(app: OrqiviumApp):
    code_based_extension.init()


code_based_extension = Extension()
