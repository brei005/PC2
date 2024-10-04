import socket
import threading

def handle_client(client_socket, target):
    # Imprime lo que el cliente envía
    request = client_socket.recv(1024)
    print("[*] Received: ", request)

    # Envía un paquete de vuelta
    client_socket.send("ACK!".encode())

    client_socket.close()

def server_loop(local_ip, local_ports, targets):
    for local_port in local_ports:
        print("[*] Trying to listen on {}:{}".format(local_ip, local_port))
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            server.bind((local_ip, local_port))
        except Exception as e:
            print("[!!] Failed to listen on {}:{}".format(local_ip, local_port))
            print("[!!] Exception: {}".format(str(e)))
            continue

        print("[*] Listening on {}:{}".format(local_ip, local_port))

        server.listen(5)

        while True:
            client_socket, addr = server.accept()

            # Crea un hilo para manejar la conexión entrante
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, targets)
            )
            client_thread.start()


def main():
    local_ip = "0.0.0.0"  # Escucha en todas las interfaces de red
    local_ports = [4343, 2343, 6231]  # Puertos en los que escucha el servidor
    targets = ["127.0.0.1", "localhost"]  # Puertos a los que se conectarán los clientes

    server_loop(local_ip, local_ports, targets)

if __name__ == "__main__":
    main()
