import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 12345))
server.listen(5)

print("Server listening...")

# Dictionary to store chat rooms and their clients
chat_rooms = {}

def handle_client(client_socket, client_room):
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            if data == "exit":
                break
            with chat_rooms[client_room]["lock"]:
                for client in chat_rooms[client_room]["clients"]:
                    client.send(data.encode())
    except Exception as e:
        print("Error:", e)
    finally:
        with chat_rooms[client_room]["lock"]:
            if client_socket in chat_rooms[client_room]["clients"]:
                chat_rooms[client_room]["clients"].remove(client_socket)
                client_socket.close()

def create_chat_room(room_id):
    chat_rooms[room_id] = {"clients": [], "lock": threading.Lock()}

try:
    while True:
        client_socket, client_address = server.accept()
        print("Accepted connection from:", client_address)
        
        option = client_socket.recv(1024).decode()  # Receive create/join option from client
        
        if option == "create":
            room_id = client_socket.recv(1024).decode()  # Receive room ID from client
            if room_id not in chat_rooms:
                create_chat_room(room_id)
                response = "Chat room created."
            else:
                response = "Chat room already exists."
        elif option == "join":
            room_id = client_socket.recv(1024).decode()  # Receive room ID from client
            if room_id in chat_rooms:
                response = "Joined chat room."
            else:
                response = "Chat room does not exist."
        else:
            response = "Invalid option."
        
        client_socket.send(response.encode())  # Send response to client
        
        if response == "Chat room created." or response == "Joined chat room.":
            with chat_rooms[room_id]["lock"]:
                chat_rooms[room_id]["clients"].append(client_socket)
            
            client_thread = threading.Thread(target=handle_client, args=(client_socket, room_id))
            client_thread.start()

except KeyboardInterrupt:
    for room_id, room_data in chat_rooms.items():
        for client_socket in room_data["clients"]:
            try:
                client_socket.send("exit".encode())  # Notify clients about server stopping
                client_socket.close()
            except Exception:
                pass
    server.close()
    print("Server stopped.")
