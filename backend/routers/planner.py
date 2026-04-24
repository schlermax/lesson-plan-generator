from flask import Blueprint, jsonify, request

planner_bp = Blueprint('planner', __name__, url_prefix='/api')


@planner_bp.route('/planner', methods=['POST'])
def planner():
    """Planner endpoint route."""
    # Implementation would reference app globals
    pass