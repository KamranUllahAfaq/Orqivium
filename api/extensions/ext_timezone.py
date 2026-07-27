import os
import time

from orqivium_app import OrqiviumApp


def init_app(app: OrqiviumApp):
    os.environ["TZ"] = "UTC"
    # windows platform not support tzset
    if hasattr(time, "tzset"):
        time.tzset()
