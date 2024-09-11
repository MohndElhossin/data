import asyncio
import websockets

async def hello():
    uri = "ws://localhost:8765"
    #uri = "127.0.0.1, 70"
    async with websockets.connect(uri) as websocket:
        name = input("what's your name? ")
    
        await websocket.send(name)
        print(f'client sent: {name}')

        greeting = await websocket.recv()
        print(f"client received: {greeting}")

if __name__ == "__main__":
    asyncio.run(hello())
