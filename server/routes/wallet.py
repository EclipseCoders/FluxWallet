from flask import Blueprint, jsonify, request
from db.database import flux_wallet_db
import uuid

routes_wallet = Blueprint('routes_wallet', __name__, url_prefix='/api/wallet/')


@routes_wallet.route('/send', methods=['POST'], strict_slashes=False)
def send():
    try:
        req = request.form
    except Exception as e:
        return jsonify({'Error': 'Invalid JSON', 'Message': str(e)}), 401

    try:
        sessionToken = request.headers.get('Authorization').replace("Token ", "").replace("Bearer ", "")
    except Exception as e:
        return jsonify({'Error': 'No Bearer', 'Message': str(e)}), 401

    session = flux_wallet_db["sessions"].find_one({"sessionToken": sessionToken})

    if session is None:
        return jsonify({"status": 401, "message": "session not found"})

    email = req.get('email')
    amount = req.get('amount')
    senderEmail = session.get('email')

    if email is None or amount is None:
        return jsonify({"status": 401}), 401

    try:
        amount = float(amount)
    except Exception as e:
        return jsonify({"status": 401}), 401

    findUserQuery = flux_wallet_db["users"].find_one({"email": senderEmail})

    findUserQueryRecipient = flux_wallet_db["users"].find_one({"email": email})

    if findUserQueryRecipient is None:
        return jsonify({"status": 401})

    if findUserQuery.get('balance') < amount:
        return jsonify({"status": 401, "message": "amount exceeds balance"})

    flux_wallet_db["users"].update_one({"email": senderEmail}, {"$inc": {"balance": -amount}})

    flux_wallet_db["users"].update_one({"email": email}, {"$inc": {"balance": amount}})

    transactionPayload = {
        "sender": findUserQuery.get("userID"),
        "recipient": email,
        "amount": amount,
        "transactionID": str(uuid.uuid4())
    }

    flux_wallet_db["transactions"].insert_one(transactionPayload)

    return jsonify({"status": 200, "message": "successfully sent"})


@routes_wallet.route('/deposit/sandbox', methods=['GET'], strict_slashes=False)
def depositSandbox():
    try:
        sessionToken = request.headers.get('Authorization').replace("Token ", "").replace("Bearer ", "")
    except Exception as e:
        return jsonify({'Error': 'No Bearer', 'Message': str(e)}), 401

    session = flux_wallet_db["sessions"].find_one({"sessionToken": sessionToken})

    if session is None:
        return jsonify({"status": 401, "message": "session not found"})

    flux_wallet_db["users"].update_one({"userID": session.get("userID")}, {"$inc": {"balance": 1000}})

    return jsonify({"status": 200, "message": "successfully deposited"})