import secrets

from flask import Flask, request, jsonify, render_template
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy import Integer, String
# from sqlalchemy.orm import Mapped, mapped_column
# import pymysql
# from ecdsa import VerifyingKey, SECP256k1
# import hashlib
import requests
import qrcode

# import settings
import wallet

app = Flask(__name__)


@app.route('/')
def index():
    private_key = request.args.get('private_key', default=None)
    if private_key:
        w = wallet.Wallet(bytes.fromhex(private_key))
    else:
        w = wallet.Wallet()
    q = qrcode.make(w.address, back_color='#00000000')
    q.save(f'static/qrcode/{w.address}.png')
    return render_template('wallet.html', address=w.address, private_key=w.private_key, public_key=w.public_key)


# @app.route('/wallet', methods=['POST'])
# def create_wallet():
#     my_wallet = wallet.Wallet()
#     response = {
#         'private_key': my_wallet.private_key,
#         'public_key': my_wallet.public_key,
#         'blockchain_address': my_wallet.address,
#     }
#     return jsonify(response), 200


@app.route('/wallet/amount', methods=['GET'])
def flask_get_amount():
    address = request.args['address']
    resp = requests.get(f"http://127.0.0.1:5555/amount?address={address}").json()
    return jsonify({
        'amount': resp["amount"]
    }), 200


@app.route('/transaction', methods=['POST'])
def flask_transaction():
    app.logger.info(request.json)
    payload = request.json
    payload["signature"] = secrets.token_urlsafe()
    resp = requests.post(f"http://127.0.0.1:5555/add_tx", json=payload)
    if resp.status_code == 200:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "fail"}), 201


def runserver():
    app.run(port=8000)


if __name__ == '__main__':
    runserver()
