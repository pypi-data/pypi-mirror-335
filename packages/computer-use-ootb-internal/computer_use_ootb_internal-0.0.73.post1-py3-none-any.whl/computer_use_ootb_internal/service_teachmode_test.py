import socketio

# Create a Socket.IO client instance
sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print("Connected to the server.")
    # Once connected, send the event to start the teachmode process:
    data = {
        "user_input": "Hello, I'd like to open the Chrome browser."
        # You can add more parameters here if needed, e.g.:
        # "model": "teach-mode-gpt-4o",
        # "task": "Some task",
        # "user_id": "my_user",
        # etc.
    }
    print("Emitting 'run_teachmode' event with data:", data)
    sio.emit("run_teachmode", data)

@sio.on('partial_response')
def on_partial_response(data):
    print("[partial_response] =>", data)

@sio.on('done')
def on_done(data):
    print("[done] =>", data)
    # Since the process is completed, you can disconnect:
    sio.disconnect()

@sio.on('disconnect')
def on_disconnect():
    print("Disconnected from server.")


if __name__ == "__main__":
    # Connect to the Socket.IO server (adapt host/port as needed):
    sio.connect("http://localhost:5001")

    # Keep the client alive to receive events
    sio.wait()
