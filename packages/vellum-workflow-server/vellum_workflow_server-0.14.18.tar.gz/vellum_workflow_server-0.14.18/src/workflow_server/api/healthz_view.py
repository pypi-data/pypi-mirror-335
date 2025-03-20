from typing import Tuple

from flask import Blueprint, Response, jsonify

bp = Blueprint("healthz", __name__)


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
def healthz() -> Tuple[Response, int]:
    resp = jsonify(success=True)
    return resp, 200
