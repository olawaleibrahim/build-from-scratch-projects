import socket
import sys
import threading


def handle_request(conn):

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            decoded_str = str(data, encoding="utf-8").split("\r\n")
            request = decoded_str[0].split(" ")
            request_type = request[0].upper()
            endpoint = request[1]
            print("decoded str", decoded_str)
            print("endpoint", endpoint)
            if endpoint == "/":
                response = "HTTP/1.1 200 OK\r\n\r\n"
            elif endpoint.startswith("/user-agent"):
                user_agent = decoded_str[-3].split(":")[-1].lstrip(" ")
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
            elif endpoint.startswith("/echo/"):
                value = endpoint.split("/echo/")[1]
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}"
            elif endpoint.startswith("/files/"):
                dir = sys.argv[2]
                filename = endpoint[7:]
                try:
                    if request_type == "POST":
                        write_data = decoded_str[-1]
                        with open(f"/{dir}/{filename}", "w") as f:
                            f.write(write_data)
                            response = f"HTTP/1.1 201 Created\r\n\r\n"

                    elif request_type == "GET":
                        with open(f"/{dir}/{filename}", "r") as f:
                            body = f.read()
                            print("body", body)
                            response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n{body}"
                except Exception as e:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
            conn.sendall(response.encode())

        except ConnectionResetError:
            break
    conn.close()


def main():
    HOST = "localhost"
    PORT = 4221
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        client_thread = threading.Thread(
            target=handle_request, args=(conn,))
        client_thread.start()


if __name__ == "__main__":
    main()
