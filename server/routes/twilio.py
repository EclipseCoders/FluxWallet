from flask import Blueprint, jsonify, request
from db.database import flux_wallet_db
import uuid

routes_twilio = Blueprint('routes_twilio', __name__, url_prefix='/api/twilio')


@routes_twilio.route('/webhook', methods=['POST'], strict_slashes=False)
def webhook():
    try:
        req = request.get_json()
    except Exception as e:
        return jsonify({'Error': 'Invalid JSON', 'Message': str(e)}), 401

    From = req.get('From')

    findUserQuery = flux_wallet_db["users"].find_one({"phone": From})

    if findUserQuery is None:
        return jsonify({"status": 401})

    Body = req.get('Body')

    command = Body.split()

    if len(command) < 3:
        return jsonify({"status": 401})

    if command[0] != "send":
        return jsonify({"status": 401})

    try:
        amount = float(command[1])
    except Exception as e:
        return jsonify({"status": 401})

    email = command[2]

    findUserQuery = flux_wallet_db["users"].find_one({"email": findUserQuery.get("email")})

    findUserQueryRecipient = flux_wallet_db["users"].find_one({"email": email})

    if findUserQueryRecipient is None:
        return jsonify({"status": 401})

    if findUserQuery.get('balance') < amount:
        return jsonify({"status": 401, "message": "amount exceeds balance"})

    flux_wallet_db["users"].update_one({"email": findUserQuery.get("email")}, {"$inc": {"balance": -amount}})

    flux_wallet_db["users"].update_one({"email": email}, {"$inc": {"balance": amount}})

    transactionPayload = {
        "sender": findUserQuery.get("userID"),
        "recipient": email,
        "amount": amount,
        "transactionID": str(uuid.uuid4())
    }

    flux_wallet_db["transactions"].insert_one(transactionPayload)

    return jsonify({"status": 201})