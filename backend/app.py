from flask import Flask, request, jsonify
from flask_sock import Sock
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
sock = Sock(app)

phone_socket = None


@app.route("/")
def home():
    return "Remote Call Backend Running"


@app.route("/call", methods=["POST"])
def call():

    global phone_socket

    if phone_socket is None:
        return jsonify({
            "success": False,
            "message": "Phone is not connected"
        }), 400

    data = request.get_json()

    number = data.get("number")

    if not number:
        return jsonify({
            "success": False,
            "message": "Phone number required"
        }), 400

    try:
        phone_socket.send(f"CALL:{number}")

        return jsonify({
            "success": True,
            "message": "Call command sent"
        })

    except Exception as e:

        phone_socket = None

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@sock.route("/phone")
def phone(ws):

    global phone_socket

    phone_socket = ws

    print("===================================")
    print("Phone Connected")
    print("===================================")

    try:

        while True:

            message = ws.receive()

            if message is None:
                break

            print("PHONE >", message)

            if message == "HELLO":
                ws.send("WELCOME")

    except Exception as e:

        print("Socket Error:", e)

    finally:

        print("===================================")
        print("Phone Disconnected")
        print("===================================")

        phone_socket = None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)