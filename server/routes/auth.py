from flask import Blueprint, jsonify, request
from db.database import flux_wallet_db
import hashlib
import jwt
import uuid

routes_auth = Blueprint('routes_auth', __name__, url_prefix='/api/auth')


@routes_auth.route('/register', methods=['POST'], strict_slashes=False)
def register():
    try:
        req = request.form
    except Exception as e:
        return jsonify({'Error': 'Invalid JSON', 'Message': str(e)}), 401

    email = req.get('email')
    password = req.get('password')
    confirmPassword = req.get('confirmPassword')

    if email is None or password is None or confirmPassword is None:
        return jsonify({"status": 401}), 401

    if password != confirmPassword:
        return jsonify({"status": 401, "message": "psswords must match"})

    findUserQuery = flux_wallet_db["users"].find_one({"email": email})

    if findUserQuery is not None:
        return jsonify({"status": 401, "message": "user already registered"}), 401

    userID = str(uuid.uuid4())

    encryptedPass = hashlib.sha256(password.encode()).hexdigest()

    userObject = {
        "email": email,
        "password": encryptedPass,
        "userID": userID,
        "balance": 0
    }

    flux_wallet_db["users"].insert_one(userObject)

    try:
        sessionToken = jwt.encode({"email": email}, str(uuid.uuid4()), algorithm="HS256").decode('UTF-8')
    except Exception as e:
        sessionToken = jwt.encode({"email": email}, str(uuid.uuid4()), algorithm="HS256")

    flux_wallet_db["sessions"].insert_one({"sessionToken": sessionToken, "email": email, "userID": userID})

    return jsonify({"status": 200, "sessionToken": sessionToken, "userID": userID})


@routes_auth.route('/', methods=['GET'], strict_slashes=False)
def getAuth():
    try:
        sessionToken = request.headers.get('Authorization').replace("Token ", "").replace("Bearer ", "")
    except Exception as e:
        return jsonify({'Error': 'No Bearer', 'Message': str(e)}), 401

    session = flux_wallet_db["sessions"].find_one({"sessionToken": sessionToken})

    if session is None:
        return jsonify({"status": 401, "message": "session not found"})

    findUserQuery = flux_wallet_db["users"].find_one({"userID": session.get("userID")})

    userID = findUserQuery.get("userID")
    balance = findUserQuery.get("balance")

    findTransactionsQuery = flux_wallet_db["transactions"].find({"sender": session.get("userID")}, {"_id": False})

    return jsonify({"status": 200, "userID": userID, "balance": balance, "transactions": list(reversed(list(findTransactionsQuery)))[0:10]})


@routes_auth.route('/login', methods=['POST'], strict_slashes=False)
def login():
    try:
        req = request.form
    except Exception as e:
        return jsonify({'Error': 'Invalid JSON', 'Message': str(e)}), 401

    email = req.get('email')
    password = req.get('password')

    if email is None or password is None:
        return jsonify({"status": 401}), 401

    findUserQuery = flux_wallet_db["users"].find_one({"email": email})

    if findUserQuery is None:
        return jsonify({"status": 401, "message": "invalid login credentials"})

    encryptedPassword = hashlib.sha256(password.encode()).hexdigest()

    if findUserQuery.get("password") == encryptedPassword:
        try:
            sessionToken = jwt.encode({"email": email}, str(uuid.uuid4()), algorithm="HS256").decode('UTF-8')
        except Exception as e:
            sessionToken = jwt.encode({"email": email}, str(uuid.uuid4()), algorithm="HS256")

        flux_wallet_db["sessions"].insert_one({"sessionToken": sessionToken, "email": email, "userID": findUserQuery.get("userID")})

        return jsonify({"status": 200, "sessionToken": sessionToken, "userID": findUserQuery.get("userID")})

    return jsonify({"status": 401, "message": "invalid login credentials"})