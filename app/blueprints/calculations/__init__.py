from flask import Blueprint

calculations_bp = Blueprint('calculations', __name__, url_prefix='/calculations')

from . import routes as routes  # noqa: F401,E402