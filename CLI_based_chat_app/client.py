import socket
import threading

# Variable to signal the thread to stop
stop_thread = threading.Event()

def receive_messages(client_socket):
    try:
        while not stop_thread.is_set():
            message = client_socket.recv(1024).decode()
            if message == "exit":
                print("Server stopped. Exiting...")
                break
            print("Received:", message)
    except ConnectionAbortedError:
        print("Connection to server lost.")
    finally:
        client_socket.close()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 12345))

try:
    option = input("Enter 'create' to create a new chat room or 'join' to join an existing chat room: ")
    client.send(option.encode())
    
    if option == "create":
        room_id = input("Enter chat room ID: ")
        client.send(room_id.encode())
        response = client.recv(1024).decode()
        print(response)
    elif option == "join":
        room_id = input("Enter chat room ID to join: ")
        client.send(room_id.encode())
        response = client.recv(1024).decode()
        print(response)
    else:
        print("Invalid option.")
        client.close()
        exit()

    if response == "Chat room created." or response == "Joined chat room.":
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.start()

        while True:
            message = input("Enter a message (type 'exit' to quit): ")
            client.send(message.encode())
            if message == "exit":
                stop_thread.set()  # Signal the thread to stop
                receive_thread.join()  # Wait for the thread to finish
                client.close()
                break
except KeyboardInterrupt:
    pass
finally:
    print("Client closed.")
