"""
AirCanvas 3D - Main entry point.

Starts camera capture, hand tracking, gesture recognition, and WebSocket server.
"""

import asyncio
import json
import time
import cv2
import signal
import sys
from typing import Set
import websockets
from websockets.server import WebSocketServerProtocol

import config
from camera import Camera
from hand_tracker import HandTracker
from gesture_engine import GestureEngine


class AirCanvas3DServer:
    """Main server coordinating camera, tracking, and WebSocket broadcasting."""
    
    def __init__(self):
        """Initialize all components."""
        self.camera = Camera()
        self.hand_tracker = HandTracker()
        self.gesture_engine = GestureEngine()
        
        self.clients: Set[WebSocketServerProtocol] = set()
        self.running = False
        self.latest_data: dict = {"t": 0, "hands": []}
        self.data_lock = asyncio.Lock()
    
    async def start(self):
        """Start all components."""
        print("=" * 60)
        print("AirCanvas 3D - Gesture-Controlled Virtual Construction")
        print("=" * 60)
        
        # Start camera
        if not self.camera.start():
            print("ERROR: Failed to start camera. Please check your webcam.")
            return False
        
        print(f"WebSocket server will start on ws://{config.WS_HOST}:{config.WS_PORT}")
        print("Waiting for browser to connect...")
        print()
        
        self.running = True
        
        # Start processing loop in background
        asyncio.create_task(self._processing_loop())
        
        # Start WebSocket server
        async with websockets.serve(
            self._handle_client,
            config.WS_HOST,
            config.WS_PORT
        ):
            await asyncio.Future()  # Run forever
        
        return True
    
    async def _processing_loop(self):
        """
        Main processing loop: capture -> detect -> classify -> broadcast.
        
        Runs at camera FPS (~30 Hz), always processes the latest frame.
        """
        print("Processing loop started")
        
        frame_count = 0
        last_time = time.time()
        
        while self.running:
            # Read latest frame
            ret, frame = self.camera.read()
            
            if not ret:
                await asyncio.sleep(0.01)
                continue
            
            # Process with MediaPipe
            results = self.hand_tracker.process(frame)
            
            # Extract landmarks
            width, height = self.camera.get_frame_size()
            hands_data = self.hand_tracker.extract_landmarks(results, width, height)
            
            # Classify gestures
            processed_hands = self.gesture_engine.process_hands(hands_data)
            
            # Build message
            message = {
                "t": time.time(),
                "hands": processed_hands
            }
            
            # Update latest data
            async with self.data_lock:
                self.latest_data = message
            
            # Broadcast to all clients
            if self.clients:
                await self._broadcast(message)
            
            # Debug visualization
            if config.SHOW_DEBUG_WINDOW:
                debug_frame = self.hand_tracker.draw_landmarks(frame.copy(), results)
                
                # Add FPS and gesture info
                fps = self.camera.get_fps()
                cv2.putText(
                    debug_frame,
                    f"FPS: {fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                
                # Show gestures
                y_offset = 60
                for hand in processed_hands:
                    text = f"{hand['handedness']}: {hand['gesture']}"
                    cv2.putText(
                        debug_frame,
                        text,
                        (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 0),
                        2
                    )
                    y_offset += 30
                
                cv2.imshow(config.DEBUG_WINDOW_NAME, debug_frame)
                
                # Check for ESC key to quit
                if cv2.waitKey(1) & 0xFF == 27:
                    print("ESC pressed, shutting down...")
                    self.running = False
                    break
            
            # Count frames for FPS
            frame_count += 1
            current_time = time.time()
            if current_time - last_time >= 5.0:
                processing_fps = frame_count / (current_time - last_time)
                print(f"Processing: {processing_fps:.1f} FPS, Clients: {len(self.clients)}")
                frame_count = 0
                last_time = current_time
            
            # Small sleep to prevent CPU overload
            await asyncio.sleep(0.001)
    
    async def _handle_client(
        self,
        websocket: WebSocketServerProtocol,
        path: str
    ):
        """
        Handle a new WebSocket client connection.
        
        Args:
            websocket: WebSocket connection
            path: Request path
        """
        client_addr = websocket.remote_address
        print(f"Client connected: {client_addr}")
        
        self.clients.add(websocket)
        
        try:
            # Send initial state
            async with self.data_lock:
                await websocket.send(json.dumps(self.latest_data))
            
            # Keep connection alive and handle incoming messages
            async for message in websocket:
                # Client can send commands if needed (future extension)
                pass
        
        except websockets.exceptions.ConnectionClosed:
            pass
        
        finally:
            self.clients.remove(websocket)
            print(f"Client disconnected: {client_addr}")
    
    async def _broadcast(self, message: dict):
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Data to broadcast
        """
        if not self.clients:
            return
        
        json_data = json.dumps(message)
        
        # Send to all clients, remove disconnected ones
        disconnected = set()
        
        for client in self.clients:
            try:
                await client.send(json_data)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Clean up disconnected clients
        self.clients -= disconnected
    
    def stop(self):
        """Stop all components."""
        print("\nShutting down...")
        self.running = False
        self.camera.stop()
        self.hand_tracker.close()
        
        if config.SHOW_DEBUG_WINDOW:
            cv2.destroyAllWindows()
        
        print("Shutdown complete")


# Global server instance for signal handler
server_instance = None


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    if server_instance:
        server_instance.stop()
    sys.exit(0)


async def main():
    """Main entry point."""
    global server_instance
    
    server_instance = AirCanvas3DServer()
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        await server_instance.start()
    except KeyboardInterrupt:
        server_instance.stop()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        server_instance.stop()


if __name__ == "__main__":
    asyncio.run(main())
