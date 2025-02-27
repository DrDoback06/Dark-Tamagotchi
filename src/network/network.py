# network.py
# Network client for the Dark Tamagotchi multiplayer functionality

import socket
import threading
import json
import time
import queue
from config import SERVER_HOST, SERVER_PORT, SOCKET_TIMEOUT

class NetworkClient:
    """Client for network communication in multiplayer mode"""
    
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        """
        Initialize the network client
        
        Parameters:
        -----------
        host : str
            Server hostname or IP address
        port : int
            Server port
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = False
        
        # Message queues
        self.send_queue = queue.Queue()
        self.receive_queue = queue.Queue()
        
        # Callbacks for different message types
        self.callbacks = {}
        
        # Threads
        self.receive_thread = None
        self.send_thread = None
        
    def connect(self):
        """
        Connect to the server
        
        Returns:
        --------
        bool
            True if connection was successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(SOCKET_TIMEOUT)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.running = True
            
            # Start threads
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            self.send_thread = threading.Thread(target=self._send_loop)
            self.send_thread.daemon = True
            self.send_thread.start()
            
            print(f"[Network] Connected to server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[Network] Connection error: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(f"[Network] Error closing socket: {e}")
                
        self.connected = False
        print("[Network] Disconnected from server")
        
    def send(self, message):
        """
        Send a message to the server
        
        Parameters:
        -----------
        message : dict or str
            Message to send
            
        Returns:
        --------
        bool
            True if message was queued, False otherwise
        """
        if not self.connected:
            print("[Network] Cannot send message: not connected")
            return False
            
        try:
            # Convert dict to JSON string if needed
            if isinstance(message, dict):
                message = json.dumps(message)
                
            # Add to queue for sending
            self.send_queue.put(message)
            return True
        except Exception as e:
            print(f"[Network] Error queueing message: {e}")
            return False
            
    def receive(self):
        """
        Get the next received message
        
        Returns:
        --------
        dict or None
            Next message from the queue, or None if queue is empty
        """
        if not self.receive_queue.empty():
            return self.receive_queue.get()
        return None
        
    def register_callback(self, message_type, callback):
        """
        Register a callback for a specific message type
        
        Parameters:
        -----------
        message_type : str
            Type of message to register for
        callback : function
            Function to call when message is received
        """
        self.callbacks[message_type] = callback
        
    def _send_loop(self):
        """Background thread for sending messages"""
        while self.running:
            try:
                # Get next message from queue with timeout
                message = self.send_queue.get(timeout=0.5)
                
                # Send the message
                self.socket.sendall((message + '\n').encode())
                print(f"[Network] Sent: {message[:100]}...")
            except queue.Empty:
                # No messages to send
                pass
            except Exception as e:
                print(f"[Network] Error sending message: {e}")
                
                # If socket error, try to reconnect
                if isinstance(e, socket.error):
                    self.connected = False
                    print("[Network] Connection lost, attempting to reconnect...")
                    try:
                        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.socket.connect((self.host, self.port))
                        self.connected = True
                        print("[Network] Reconnected to server")
                    except Exception as reconnect_error:
                        print(f"[Network] Failed to reconnect: {reconnect_error}")
                        time.sleep(5)  # Wait before next attempt
                        
    def _receive_loop(self):
        """Background thread for receiving messages"""
        buffer = ""
        
        while self.running:
            try:
                # Receive data
                data = self.socket.recv(4096)
                
                if not data:
                    # Connection closed by server
                    print("[Network] Connection closed by server")
                    self.connected = False
                    break
                    
                # Decode and add to buffer
                buffer += data.decode()
                
                # Process complete messages
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    try:
                        # Parse JSON message
                        message_obj = json.loads(message)
                        
                        # Add to queue
                        self.receive_queue.put(message_obj)
                        
                        # Call registered callback if any
                        message_type = message_obj.get("type", "")
                        if message_type in self.callbacks:
                            self.callbacks[message_type](message_obj)
                            
                        print(f"[Network] Received: {message[:100]}...")
                    except json.JSONDecodeError:
                        print(f"[Network] Error decoding JSON: {message}")
                        
            except socket.timeout:
                # Socket timeout is normal
                continue
            except Exception as e:
                print(f"[Network] Error receiving data: {e}")
                # If socket error, connection is lost
                if isinstance(e, socket.error):
                    self.connected = False
                    print("[Network] Connection lost")
                    break
                    
        # If we exited the loop but still running, try to reconnect
        if self.running and not self.connected:
            print("[Network] Attempting to reconnect...")
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.connected = True
                print("[Network] Reconnected to server")
                # Restart receive loop
                self.receive_thread = threading.Thread(target=self._receive_loop)
                self.receive_thread.daemon = True
                self.receive_thread.start()
            except Exception as reconnect_error:
                print(f"[Network] Failed to reconnect: {reconnect_error}")
                
    # ===== High-level network functions =====
    
    def join_lobby(self, creature):
        """
        Join the multiplayer lobby
        
        Parameters:
        -----------
        creature : Creature
            The player's creature
            
        Returns:
        --------
        bool
            True if request was sent, False otherwise
        """
        message = {
            "type": "JOIN_LOBBY",
            "creature": creature.to_dict(),
            "timestamp": time.time()
        }
        return self.send(message)
        
    def leave_lobby(self):
        """
        Leave the multiplayer lobby
        
        Returns:
        --------
        bool
            True if request was sent, False otherwise
        """
        message = {
            "type": "LEAVE_LOBBY",
            "timestamp": time.time()
        }
        return self.send(message)
        
    def send_battle_action(self, ability_index):
        """
        Send a battle action
        
        Parameters:
        -----------
        ability_index : int
            Index of the ability to use
            
        Returns:
        --------
        bool
            True if request was sent, False otherwise
        """
        message = {
            "type": "BATTLE_ACTION",
            "ability_index": ability_index,
            "timestamp": time.time()
        }
        return self.send(message)
        
    def create_adventure_party(self, creature):
        """
        Create an adventure party
        
        Parameters:
        -----------
        creature : Creature
            The player's creature
            
        Returns:
        --------
        bool
            True if request was sent, False otherwise
        """
        message = {
            "type": "CREATE_ADVENTURE",
            "creature": creature.to_dict(),
            "timestamp": time.time()
        }
        return self.send(message)
        
    def join_adventure_party(self, party_id, creature):
        """
        Join an adventure party
        
        Parameters:
        -----------
        party_id : str
            ID of the party to join
        creature : Creature
            The player's creature
            
        Returns:
        --------
        bool
            True if request was sent, False otherwise
        """
        message = {
            "type": "JOIN_ADVENTURE",
            "party_id": party_id,
            "creature": creature.to_dict(),
            "timestamp": time.time()
        }
        return self.send(message)
        
    def send_adventure_update(self, adventure_data):
        """
        Send adventure update data
        
        Parameters:
        -----------
        adventure_data : dict
            Adventure update data
            
        Returns:
        --------
        bool
            True if request was sent, False otherwise
        """
        message = {
            "type": "ADVENTURE_UPDATE",
            "data": adventure_data,
            "timestamp": time.time()
        }
        return self.send(message)
        
    def request_available_parties(self):
        """
        Request list of available adventure parties
        
        Returns:
        --------
        bool
            True if request was sent, False otherwise
        """
        message = {
            "type": "GET_ADVENTURE_PARTIES",
            "timestamp": time.time()
        }
        return self.send(message)
