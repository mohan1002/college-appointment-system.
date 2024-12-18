from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import db
from .models import User, Availability, Appointment

api = Blueprint('api', __name__)

@api.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password, role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@api.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"message": "Invalid credentials"}), 401
    token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({"token": token})

@api.route('/availability', methods=['POST'])
@jwt_required()
def set_availability():
    user = get_jwt_identity()
    if user['role'] != 'professor':
        return jsonify({"message": "Unauthorized"}), 403
    data = request.json
    for slot in data['time_slots']:
        new_availability = Availability(professor_id=user['id'], time_slot=slot)
        db.session.add(new_availability)
    db.session.commit()
    return jsonify({"message": "Availability set successfully"})

@api.route('/slots/<int:professor_id>', methods=['GET'])
@jwt_required()
def get_slots(professor_id):
    slots = Availability.query.filter_by(professor_id=professor_id, is_booked=False).all()
    return jsonify([slot.time_slot for slot in slots])

@api.route('/book', methods=['POST'])
@jwt_required()
def book_slot():
    user = get_jwt_identity()
    if user['role'] != 'student':
        return jsonify({"message": "Unauthorized"}), 403
    data = request.json
    slot = Availability.query.filter_by(id=data['slot_id'], is_booked=False).first()
    if not slot:
        return jsonify({"message": "Slot unavailable"}), 400
    new_appointment = Appointment(student_id=user['id'], professor_id=slot.professor_id, time_slot=slot.time_slot)
    slot.is_booked = True
    db.session.add(new_appointment)
    db.session.commit()
    return jsonify({"message": "Appointment booked successfully"})
