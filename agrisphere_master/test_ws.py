import asyncio
import websockets
import json

async def test_chatbot():
    uri = "ws://localhost:8000/ws/master-chat"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Receive welcome message
            greeting = await websocket.recv()
            print(f"< {json.loads(greeting)['message']}")

            queries = [
                "What is the current soil moisture?", # Tests Sensor Agent
                "Is there a flood risk in Tamil Nadu?", # Tests Climate Agent
                "Are my tomatoes safe?" # Tests Cross-Tier (Sensor + Climate + Plant)
            ]

            for query in queries:
                print(f"\n> {query}")
                await websocket.send(query)
                
                # Receive "Analyzing..." message
                analyzing = await websocket.recv()
                print(f"< {json.loads(analyzing)['message']}")
                
                # Receive final synthesis
                final_answer = await websocket.recv()
                print(f"< {json.loads(final_answer)['message']}")
                
                await asyncio.sleep(2)

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_chatbot())
