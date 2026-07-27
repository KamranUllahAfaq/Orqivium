from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Flask

if TYPE_CHECKING:
    from extensions.ext_login import OrqiviumLoginManager


class OrqiviumApp(Flask):
    """Flask application type with Orqivium-specific extension attributes."""

    login_manager: OrqiviumLoginManager
