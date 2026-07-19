import threading

from flask import Flask, request, jsonify
from flask_sock import Sock
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# 25s ping keeps the connection alive through Render's proxy, which
# otherwise drops idle sockets.
app.config["SOCK_SERVER_OPTIONS"] = {"ping_interval": 25}
sock = Sock(app)

phone_socket = None
# Guards phone_socket since the websocket handler and the /call route
# now run concurrently (eventlet greenlets) instead of one-at-a-time.
phone_lock = threading.Lock()


@app.route("/")
def home():
    return "Remote Call Backend Running"


@app.route("/status")
def status():
    with phone_lock:
        connected = phone_socket is not None
    return jsonify({"phone_connected": connected})


@app.route("/call", methods=["POST"])
def call():

    global phone_socket

    with phone_lock:
        ws = phone_socket

    if ws is None:
        return jsonify({
            "success": False,
            "message": "Phone is not connected"
        }), 400

    data = request.get_json(silent=True) or {}

    number = data.get("number")

    if not number:
        return jsonify({
            "success": False,
            "message": "Phone number required"
        }), 400

    try:
        ws.send(f"CALL:{number}")

        return jsonify({
            "success": True,
            "message": "Call command sent"
        })

    except Exception as e:

        with phone_lock:
            phone_socket = None

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@sock.route("/phone")
def phone(ws):

    global phone_socket

    with phone_lock:
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
            elif message == "PING":
                ws.send("PONG")

    except Exception as e:

        print("Socket Error:", e)

    finally:

        print("===================================")
        print("Phone Disconnected")
        print("===================================")

        with phone_lock:
            if phone_socket is ws:
                phone_socket = None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)