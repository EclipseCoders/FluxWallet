from flask import Flask
from flask_cors import CORS
from routes.auth import routes_auth
from routes.wallet import routes_wallet
from routes.twilio import routes_twilio

app = Flask(__name__)
CORS(app)

app.register_blueprint(routes_auth)
app.register_blueprint(routes_wallet)
app.register_blueprint(routes_twilio)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)