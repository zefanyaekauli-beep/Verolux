#!/usr/bin/env python3
"""
Test WebSocket connection to the backend server
"""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8002/ws"
    
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Wait for messages
            for i in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    print(f"📨 Received message {i+1}: {data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'detection':
                        detections = data.get('detections', [])
                        print(f"   Detections: {len(detections)} objects")
                        
                    if data.get('body_checking_alert'):
                        print(f"   🚨 Alert: {data['body_checking_alert']['message']}")
                        
                except asyncio.TimeoutError:
                    print(f"⏰ Timeout waiting for message {i+1}")
                    break
                except Exception as e:
                    print(f"❌ Error receiving message {i+1}: {e}")
                    break
                    
            print("✅ WebSocket test completed successfully!")
            
    except ConnectionRefusedError:
        print("❌ Connection refused - server not running")
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
