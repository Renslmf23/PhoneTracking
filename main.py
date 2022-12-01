from WebsocketServer import WebSocketServer

if __name__ == "__main__":
    server = WebSocketServer("localhost", 11225)
    server.start()
