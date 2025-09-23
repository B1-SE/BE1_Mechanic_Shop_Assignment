"""
Members routes (alias for customers with membership features).
"""

from flask import Blueprint

# Create members blueprint as an alias to customers
members_bp = Blueprint("members", __name__)

# You can add member-specific routes here or alias existing customer routes


def register_blueprints(app):
    """Register application blueprints."""
    # ...existing code...

    # Debug route to see all registered routes
    @app.route("/debug/routes")
    def list_routes():
        """List all registered routes for debugging."""
        import urllib.parse

        output = []
        for rule in app.url_map.iter_rules():
            methods = ",".join(rule.methods)
            line = urllib.parse.unquote(f"{rule.endpoint}: {rule.rule} [{methods}]")
            output.append(line)
        return {"routes": output}
