from flask import Flask, request, jsonify
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

# Stores the connected Android phone
phone_socket = None


@app.route("/")
def home():
    return "Remote Call Backend Running"


# Called by the web app
@app.route("/call", methods=["POST"])
def make_call():
    global phone_socket

    if phone_socket is None:
        return jsonify({
            "success": False,
            "message": "Phone is not connected"
        }), 400

    data = request.json
    number = data.get("number")

    if not number:
        return jsonify({
            "success": False,
            "message": "Phone number required"
        }), 400

    phone_socket.send(f"CALL:{number}")

    return jsonify({
        "success": True,
        "message": "Call command sent"
    })


# Android connects here
@sock.route("/phone")
def phone(ws):
    global phone_socket

    phone_socket = ws
    print("Phone Connected")

    try:
        while True:
            message = ws.receive()

            if message is None:
                break

            print("Phone:", message)

    except Exception as e:
        print(e)

    finally:
        phone_socket = None
        print("Phone Disconnected")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)