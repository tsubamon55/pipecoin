import secrets
import wallet
import qrcode

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import pymysql

import settings


class Base(DeclarativeBase):
    pass


pymysql.install_as_MySQLdb()

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+pymysql://{settings.user}:{settings.password}@{settings.host}/pipecoin'
# initialize the app with the extension
db.init_app(app)

memory_pool = []


class Transaction(db.Model):
    __tablename__ = "transaction"
    txid = db.Column(db.String, primary_key=True)
    sender = db.Column(db.String)
    pubkey = db.Column(db.String)
    signature = db.Column(db.String)
    recipient = db.Column(db.String)
    amount = db.Column(db.Float)


class Ledger(db.Model):
    __tablename__ = "ledger"
    address = db.Column(db.String, primary_key=True)
    amount = db.Column(db.Float)


class Block(db.Model):
    __tablename__ = "block"
    n = db.Column(db.Integer, primary_key=True, autoincrement=True)
    previous_hash = db.Column(db.String)
    merkle_root = db.Column(db.String)
    nonce = db.Column(db.String)
    timestamp = db.Column(db.DateTime)


@app.route("/add_tx", methods=["GET", "POST"])
def flask_mempool():
    if request.method == "POST":
        resp = request.json
        txid = secrets.token_urlsafe()
        app.logger.info(resp)
        app.logger.info(resp)
        tx = Transaction(txid=txid, sender=resp["sender_address"], pubkey=resp["public_key"], signature=resp["signature"], recipient=resp["recipient_address"], amount=resp["amount"])
        # if not tx.verify():
        #     return "署名が不正です"

        sender = Ledger.query.get(resp["sender_address"])
        recipient = Ledger.query.get(resp["recipient_address"])
        if not sender:
            return "アカウントがありません"
        if not recipient:
            ledger = Ledger(address=resp["recipient_address"], amount=0)
            db.session.add(ledger)
            db.session.commit()
            recipient = Ledger.query.get(resp["recipient_address"])
        sender.amount -= float(resp["amount"])
        recipient.amount += float(resp["amount"])
        db.session.add(tx)
        db.session.commit()
        return "トランザクションが追加されました"
    if request.method == "GET":
        return memory_pool


@app.route("/add_block", methods=["POST"])
def flask_add_block():
    resp = request.json
    block = Block(previous_hash=resp["previous_hash"], merkle_root=resp["merkle_root"],
                  nonce=resp["nonce"], timestamp=resp["timestamp"])
    db.session.add(block)
    db.session.commit()
    return "ブロックが追加されました"


@app.route('/amount', methods=['GET'])
def get_total_amount():
    address = request.args['address']
    column = Ledger.query.get(address)
    if not column:
        return jsonify({'amount': 0}), 201
    return jsonify({
        'amount': column.amount
    }), 200


@app.route('/c', methods=['GET'])
def flask_coldwallet():
    session = secrets.token_urlsafe(16)
    w = wallet.Wallet()
    ledger1 = Ledger(address=w.address, amount=10)
    db.session.add(ledger1)
    db.session.commit()
    url = f'http://157.7.212.250/pipecoin/wallet?private_key={w.private_key}'
    qr = qrcode.make(url)
    qr.save(f'code/{session}.png')
    return 'success'


if __name__ == '__main__':
    app.run(port=5555, debug=True)
