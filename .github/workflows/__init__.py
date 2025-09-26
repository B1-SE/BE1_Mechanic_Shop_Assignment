"""
Mechanics blueprint package.
"""

from flask import Blueprint

mechanics_bp = Blueprint("mechanics", __name__)

from . import routes  # noqa: F401, E402
