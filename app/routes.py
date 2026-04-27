"""HTTP routes for the ACEest Fitness & Gym service (v1.0)."""
from __future__ import annotations

from flask import Flask, jsonify, request

from .programs import PROGRAMS, estimate_calories


def register_routes(app: Flask) -> None:
    @app.get("/")
    def home():
        return (
            "<h1>ACEest Fitness &amp; Gym</h1>"
            f"<p>Version {app.config['VERSION']} - Programs Catalog</p>"
            "<ul>"
            "<li>GET /health</li>"
            "<li>GET /version</li>"
            "<li>GET /programs</li>"
            "<li>GET /programs/&lt;key&gt;  (FL | MG | BG)</li>"
            "<li>GET /calories?weight=70&program=MG</li>"
            "</ul>"
        )

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.get("/version")
    def version():
        return jsonify(version=app.config["VERSION"]), 200

    @app.get("/programs")
    def list_programs():
        return jsonify(list(PROGRAMS.values())), 200

    @app.get("/programs/<key>")
    def get_program(key: str):
        program = PROGRAMS.get(key.upper())
        if not program:
            return jsonify(error=f"unknown program: {key}"), 404
        return jsonify(program), 200

    @app.get("/calories")
    def calories():
        try:
            weight = float(request.args.get("weight", ""))
            program_key = request.args.get("program", "").upper()
            kcal = estimate_calories(weight, program_key)
        except (ValueError, KeyError) as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(weight=weight, program=program_key, calories=kcal), 200
