import asyncio
import websockets
import ssl

# Define SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile="/home/SEI/Desktop/cert/certificate.pem", keyfile="/home/SEI/Desktop/cert/private_key.pem")

async def hello(websocket):
    try:
        while True:  # Continuous loop to handle multiple messages
            data = await websocket.recv()
            print(f'Server Received: {data}')
            greeting = f'{data}!'
            await websocket.send(greeting)
            print(f'Server Sent: {greeting}')
    except websockets.ConnectionClosed:
        print("Connection closed")
    except Exception as e:
        print(f"An error occurred: {e}")

async def server_main():
    async with websockets.serve(hello, "192.168.25.143",443, ssl=ssl_context, ping_interval=60, ping_timeout=60):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(server_main())
