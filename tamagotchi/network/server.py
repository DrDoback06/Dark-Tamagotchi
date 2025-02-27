# server.py
# Multiplayer server for Dark Tamagotchi

import socket
import threading
import json
import time
import uuid
from tamagotchi.utils.config import SERVER_HOST, SERVER_PORT

class ClientHandler:
    """Handler for a client connection"""
    
    def __init__(self, server, conn, addr):
        """
        Initialize a client handler
        
        Parameters:
        -----------
        server : GameServer
            The game server
        conn : socket
            Client socket connection
        addr : tuple
            Client address
        """
        self.server = server
        self.conn = conn
        self.addr = addr
        self.running = True
        self.player_id = str(uuid.uuid4())
        self.username = f"Player_{self.player_id[:8]}"
        self.creature = None
        
        # Client state
        self.in_lobby = False
        self.in_battle = False
        self.battle_id = None
        self.in_adventure = False
        self.adventure_id = None
        
        print(f"[Server] Client connected: {addr} (ID: {self.player_id})")
        
    def run(self):
        """Handle client communications"""
        buffer = ""
        
        while self.running:
            try:
                # Receive data
                data = self.conn.recv(4096)
                
                if not data:
                    # Connection closed
                    break
                    
                # Decode and add to buffer
                buffer += data.decode()
                
                # Process complete messages
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    self.process_message(message)
                    
            except Exception as e:
                print(f"[Server] Error handling client {self.addr}: {e}")
                break
                
        # Clean up when client disconnects
        print(f"[Server] Client disconnected: {self.addr} (ID: {self.player_id})")
        self.clean_up()
        
    def clean_up(self):
        """Clean up when client disconnects"""
        # Remove from lobby
        if self.in_lobby:
            self.server.remove_from_lobby(self)
            
        # Remove from battle
        if self.in_battle:
            self.server.end_battle(self.battle_id, self.player_id)
            
        # Remove from adventure
        if self.in_adventure:
            self.server.remove_from_adventure(self.adventure_id, self.player_id)
            
        # Close connection
        try:
            self.conn.close()
        except Exception:
            pass
            
        self.running = False
        
    def process_message(self, message):
        """
        Process a client message
        
        Parameters:
        -----------
        message : str
            JSON message from client
        """
        try:
            # Parse JSON message
            data = json.loads(message)
            message_type = data.get("type", "")
            
            print(f"[Server] Received from {self.addr} (ID: {self.player_id}): {message_type}")
            
            # Handle different message types
            if message_type == "JOIN_LOBBY":
                self.handle_join_lobby(data)
            elif message_type == "LEAVE_LOBBY":
                self.handle_leave_lobby()
            elif message_type == "BATTLE_ACTION":
                self.handle_battle_action(data)
            elif message_type == "CREATE_ADVENTURE":
                self.handle_create_adventure(data)
            elif message_type == "JOIN_ADVENTURE":
                self.handle_join_adventure(data)
            elif message_type == "ADVENTURE_UPDATE":
                self.handle_adventure_update(data)
            elif message_type == "GET_ADVENTURE_PARTIES":
                self.handle_get_adventure_parties()
            else:
                print(f"[Server] Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            print(f"[Server] Error decoding JSON: {message}")
        except Exception as e:
            print(f"[Server] Error processing message: {e}")
            
    def send(self, message):
        """
        Send a message to the client
        
        Parameters:
        -----------
        message : dict or str
            Message to send
            
        Returns:
        --------
        bool
            True if sent successfully, False otherwise
        """
        try:
            # Convert dict to JSON string if needed
            if isinstance(message, dict):
                message = json.dumps(message)
                
            # Send with newline terminator
            self.conn.sendall((message + '\n').encode())
            return True
        except Exception as e:
            print(f"[Server] Error sending to client {self.addr}: {e}")
            return False
            
    # ===== Message handlers =====
    
    def handle_join_lobby(self, data):
        """
        Handle JOIN_LOBBY message
        
        Parameters:
        -----------
        data : dict
            Message data
        """
        # Extract creature data
        creature_data = data.get("creature", {})
        self.creature = creature_data
        
        # Extract username if provided
        if "username" in data:
            self.username = data["username"]
            
        # Add to lobby
        self.server.add_to_lobby(self)
        self.in_lobby = True
        
        # Confirm joined
        self.send({
            "type": "LOBBY_JOINED",
            "player_id": self.player_id,
            "username": self.username,
            "players_waiting": self.server.get_lobby_count()
        })
        
    def handle_leave_lobby(self):
        """Handle LEAVE_LOBBY message"""
        if self.in_lobby:
            self.server.remove_from_lobby(self)
            self.in_lobby = False
            
            # Confirm left
            self.send({
                "type": "LOBBY_LEFT",
                "player_id": self.player_id
            })
            
    def handle_battle_action(self, data):
        """
        Handle BATTLE_ACTION message
        
        Parameters:
        -----------
        data : dict
            Message data
        """
        if not self.in_battle:
            print(f"[Server] Client {self.player_id} not in battle")
            return
            
        # Forward action to battle handler
        ability_index = data.get("ability_index", 0)
        self.server.process_battle_action(self.battle_id, self.player_id, ability_index)
        
    def handle_create_adventure(self, data):
        """
        Handle CREATE_ADVENTURE message
        
        Parameters:
        -----------
        data : dict
            Message data
        """
        # Extract creature data
        creature_data = data.get("creature", {})
        self.creature = creature_data
        
        # Create adventure party
        adventure_id = self.server.create_adventure_party(self)
        self.adventure_id = adventure_id
        self.in_adventure = True
        
        # Confirm creation
        self.send({
            "type": "ADVENTURE_CREATED",
            "adventure_id": adventure_id,
            "player_id": self.player_id
        })
        
    def handle_join_adventure(self, data):
        """
        Handle JOIN_ADVENTURE message
        
        Parameters:
        -----------
        data : dict
            Message data
        """
        # Extract creature data and party ID
        creature_data = data.get("creature", {})
        self.creature = creature_data
        party_id = data.get("party_id", "")
        
        # Join adventure party
        success = self.server.join_adventure_party(party_id, self)
        
        if success:
            self.adventure_id = party_id
            self.in_adventure = True
            
            # Confirm joined
            self.send({
                "type": "ADVENTURE_JOINED",
                "adventure_id": party_id,
                "player_id": self.player_id
            })
        else:
            # Failed to join
            self.send({
                "type": "ADVENTURE_JOIN_FAILED",
                "adventure_id": party_id,
                "message": "Failed to join adventure party"
            })
            
    def handle_adventure_update(self, data):
        """
        Handle ADVENTURE_UPDATE message
        
        Parameters:
        -----------
        data : dict
            Message data
        """
        if not self.in_adventure:
            print(f"[Server] Client {self.player_id} not in adventure")
            return
            
        # Forward update to adventure handler
        update_data = data.get("data", {})
        self.server.process_adventure_update(self.adventure_id, self.player_id, update_data)
        
    def handle_get_adventure_parties(self):
        """Handle GET_ADVENTURE_PARTIES message"""
        # Get active adventure parties
        parties = self.server.get_adventure_parties()
        
        # Send list to client
        self.send({
            "type": "ADVENTURE_PARTIES",
            "parties": parties
        })

class GameServer:
    """Main game server class"""
    
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        """
        Initialize the game server
        
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
        self.running = False
        
        # Client connections
        self.clients = {}  # player_id -> ClientHandler
        
        # Game state
        self.lobby = []  # List of clients waiting for battles
        self.battles = {}  # battle_id -> battle_data
        self.adventure_parties = {}  # adventure_id -> party_data
        
    def start(self):
        """Start the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print(f"[Server] Server started on {self.host}:{self.port}")
            
            # Start matchmaking thread
            matchmaking_thread = threading.Thread(target=self.matchmaking_loop)
            matchmaking_thread.daemon = True
            matchmaking_thread.start()
            
            # Main accept loop
            self.accept_connections()
            
        except Exception as e:
            print(f"[Server] Error starting server: {e}")
            
    def accept_connections(self):
        """Accept client connections"""
        while self.running:
            try:
                # Accept new connection
                conn, addr = self.socket.accept()
                
                # Create handler for client
                client = ClientHandler(self, conn, addr)
                self.clients[client.player_id] = client
                
                # Start client thread
                client_thread = threading.Thread(target=client.run)
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                print(f"[Server] Error accepting connection: {e}")
                
    def stop(self):
        """Stop the server"""
        self.running = False
        
        # Close all client connections
        for client in list(self.clients.values()):
            try:
                client.running = False
                client.conn.close()
            except Exception:
                pass
                
        # Close server socket
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
                
        print("[Server] Server stopped")
        
    def matchmaking_loop(self):
        """Background thread for matchmaking"""
        while self.running:
            try:
                # Match players in lobby
                self.match_players()
                
                # Sleep to avoid CPU usage
                time.sleep(1)
            except Exception as e:
                print(f"[Server] Error in matchmaking: {e}")
                
    def match_players(self):
        """Match players in the lobby for battles"""
        if len(self.lobby) < 2:
            return
            
        # Simple matching: take first two players
        player1 = self.lobby[0]
        player2 = self.lobby[1]
        
        # Remove from lobby
        self.remove_from_lobby(player1)
        self.remove_from_lobby(player2)
        
        # Create battle
        battle_id = str(uuid.uuid4())
        battle_data = {
            "id": battle_id,
            "player1": player1.player_id,
            "player2": player2.player_id,
            "creature1": player1.creature,
            "creature2": player2.creature,
            "current_turn": "player1",
            "start_time": time.time(),
            "last_activity": time.time()
        }
        
        self.battles[battle_id] = battle_data
        
        # Update client state
        player1.in_battle = True
        player1.battle_id = battle_id
        player2.in_battle = True
        player2.battle_id = battle_id
        
        # Notify players
        player1.send({
            "type": "BATTLE_START",
            "battle_id": battle_id,
            "your_role": "player1",
            "player_creature": player1.creature,
            "opponent_creature": player2.creature,
            "current_turn": "player1"
        })
        
        player2.send({
            "type": "BATTLE_START",
            "battle_id": battle_id,
            "your_role": "player2",
            "player_creature": player2.creature,
            "opponent_creature": player1.creature,
            "current_turn": "player1"
        })
        
        print(f"[Server] Battle started: {battle_id} ({player1.player_id} vs {player2.player_id})")
        
    # ===== Lobby management =====
    
    def add_to_lobby(self, client):
        """
        Add a client to the lobby
        
        Parameters:
        -----------
        client : ClientHandler
            Client to add to lobby
        """
        if client not in self.lobby:
            self.lobby.append(client)
            print(f"[Server] Client {client.player_id} joined lobby")
            
            # Notify all clients in lobby
            self.broadcast_lobby_status()
            
    def remove_from_lobby(self, client):
        """
        Remove a client from the lobby
        
        Parameters:
        -----------
        client : ClientHandler
            Client to remove from lobby
        """
        if client in self.lobby:
            self.lobby.remove(client)
            print(f"[Server] Client {client.player_id} left lobby")
            
            # Notify all clients in lobby
            self.broadcast_lobby_status()
            
    def get_lobby_count(self):
        """
        Get the number of clients in the lobby
        
        Returns:
        --------
        int
            Number of clients in the lobby
        """
        return len(self.lobby)
        
    def broadcast_lobby_status(self):
        """Broadcast lobby status to all clients in lobby"""
        status = {
            "type": "LOBBY_STATUS",
            "players_waiting": len(self.lobby),
            "timestamp": time.time()
        }
        
        for client in self.lobby:
            client.send(status)
            
    # ===== Battle management =====
    
    def process_battle_action(self, battle_id, player_id, ability_index):
        """
        Process a battle action
        
        Parameters:
        -----------
        battle_id : str
            ID of the battle
        player_id : str
            ID of the player making the action
        ability_index : int
            Index of the ability to use
        """
        if battle_id not in self.battles:
            print(f"[Server] Battle {battle_id} not found")
            return
            
        battle = self.battles[battle_id]
        battle["last_activity"] = time.time()
        
        # Determine roles
        player_role = "player1" if player_id == battle["player1"] else "player2"
        opponent_role = "player2" if player_role == "player1" else "player1"
        opponent_id = battle["player2"] if player_role == "player1" else battle["player1"]
        
        # Verify it's this player's turn
        if battle["current_turn"] != player_role:
            print(f"[Server] Not {player_id}'s turn in battle {battle_id}")
            return
            
        # Get the opponent
        if opponent_id not in self.clients:
            print(f"[Server] Opponent {opponent_id} not found")
            self.end_battle(battle_id, player_id)
            return
            
        opponent = self.clients[opponent_id]
        
        # Update battle state
        battle["current_turn"] = opponent_role
        
        # Forward action to opponent
        action_data = {
            "type": "BATTLE_ACTION",
            "battle_id": battle_id,
            "ability_index": ability_index,
            "current_turn": opponent_role
        }
        
        opponent.send(action_data)
        
        print(f"[Server] Battle {battle_id}: {player_id} used ability {ability_index}")
        
    def end_battle(self, battle_id, player_id=None):
        """
        End a battle
        
        Parameters:
        -----------
        battle_id : str
            ID of the battle to end
        player_id : str, optional
            ID of the player who ended the battle (if defeated or disconnected)
        """
        if battle_id not in self.battles:
            return
            
        battle = self.battles[battle_id]
        
        # Determine winner if a player ended the battle
        winner_role = None
        winner_id = None
        
        if player_id:
            winner_role = "player2" if player_id == battle["player1"] else "player1"
            winner_id = battle["player2"] if winner_role == "player2" else battle["player1"]
            
        # Clean up battle
        player1_id = battle["player1"]
        player2_id = battle["player2"]
        
        # Notify players
        for pid in [player1_id, player2_id]:
            if pid in self.clients:
                client = self.clients[pid]
                
                if client.in_battle and client.battle_id == battle_id:
                    client.in_battle = False
                    client.battle_id = None
                    
                    # Send battle end notification
                    client.send({
                        "type": "BATTLE_END",
                        "battle_id": battle_id,
                        "winner": winner_role,
                        "reason": "disconnect" if player_id else "completion"
                    })
                    
        # Remove battle
        del self.battles[battle_id]
        print(f"[Server] Battle {battle_id} ended")
        
    # ===== Adventure management =====
    
    def create_adventure_party(self, client):
        """
        Create an adventure party
        
        Parameters:
        -----------
        client : ClientHandler
            Client creating the party
            
        Returns:
        --------
        str
            ID of the created adventure party
        """
        adventure_id = str(uuid.uuid4())
        
        # Create party data
        party_data = {
            "id": adventure_id,
            "host": client.player_id,
            "members": [client.player_id],
            "creatures": [client.creature],
            "usernames": [client.username],
            "state": "waiting",
            "creation_time": time.time(),
            "last_activity": time.time()
        }
        
        self.adventure_parties[adventure_id] = party_data
        
        print(f"[Server] Adventure party created: {adventure_id} (host: {client.player_id})")
        
        return adventure_id
        
    def join_adventure_party(self, party_id, client):
        """
        Join an adventure party
        
        Parameters:
        -----------
        party_id : str
            ID of the party to join
        client : ClientHandler
            Client joining the party
            
        Returns:
        --------
        bool
            True if joined successfully, False otherwise
        """
        if party_id not in self.adventure_parties:
            print(f"[Server] Adventure party {party_id} not found")
            return False
            
        party = self.adventure_parties[party_id]
        
        # Check if party is full
        if len(party["members"]) >= 4:
            print(f"[Server] Adventure party {party_id} is full")
            return False
            
        # Check if party is still waiting
        if party["state"] != "waiting":
            print(f"[Server] Adventure party {party_id} is not accepting new members")
            return False
            
        # Add client to party
        party["members"].append(client.player_id)
        party["creatures"].append(client.creature)
        party["usernames"].append(client.username)
        party["last_activity"] = time.time()
        
        print(f"[Server] Client {client.player_id} joined adventure party {party_id}")
        
        # Notify all party members
        self.broadcast_adventure_update(party_id)
        
        # If party now has enough members, start the adventure
        if len(party["members"]) >= 2:
            party["state"] = "active"
            
            # Notify all party members
            self.broadcast_adventure_start(party_id)
            
        return True
        
    def remove_from_adventure(self, adventure_id, player_id):
        """
        Remove a player from an adventure party
        
        Parameters:
        -----------
        adventure_id : str
            ID of the adventure party
        player_id : str
            ID of the player to remove
        """
        if adventure_id not in self.adventure_parties:
            return
            
        party = self.adventure_parties[adventure_id]
        
        # Check if player is in party
        if player_id not in party["members"]:
            return
            
        # Get index of player
        index = party["members"].index(player_id)
        
        # Remove player from party
        party["members"].pop(index)
        party["creatures"].pop(index)
        party["usernames"].pop(index)
        party["last_activity"] = time.time()
        
        print(f"[Server] Client {player_id} left adventure party {adventure_id}")
        
        # If party is now empty, remove it
        if not party["members"]:
            del self.adventure_parties[adventure_id]
            print(f"[Server] Adventure party {adventure_id} removed (empty)")
            return
            
        # If host left, assign new host
        if player_id == party["host"]:
            party["host"] = party["members"][0]
            print(f"[Server] New host for adventure party {adventure_id}: {party['host']}")
            
        # Notify remaining party members
        self.broadcast_adventure_update(adventure_id)
        
    def process_adventure_update(self, adventure_id, player_id, update_data):
        """
        Process an adventure update
        
        Parameters:
        -----------
        adventure_id : str
            ID of the adventure party
        player_id : str
            ID of the player sending the update
        update_data : dict
            Update data
        """
        if adventure_id not in self.adventure_parties:
            print(f"[Server] Adventure party {adventure_id} not found")
            return
            
        party = self.adventure_parties[adventure_id]
        
        # Check if player is in party
        if player_id not in party["members"]:
            print(f"[Server] Client {player_id} not in adventure party {adventure_id}")
            return
            
        # Update last activity time
        party["last_activity"] = time.time()
        
        # Forward update to all party members
        update_message = {
            "type": "ADVENTURE_UPDATE",
            "adventure_id": adventure_id,
            "from_player": player_id,
            "data": update_data,
            "timestamp": time.time()
        }
        
        for member_id in party["members"]:
            if member_id != player_id and member_id in self.clients:
                member = self.clients[member_id]
                member.send(update_message)
                
        print(f"[Server] Adventure {adventure_id}: Update from {player_id}")
        
    def broadcast_adventure_update(self, adventure_id):
        """
        Broadcast an adventure update to all party members
        
        Parameters:
        -----------
        adventure_id : str
            ID of the adventure party
        """
        if adventure_id not in self.adventure_parties:
            return
            
        party = self.adventure_parties[adventure_id]
        
        # Create update message
        update = {
            "type": "ADVENTURE_PARTY_UPDATE",
            "adventure_id": adventure_id,
            "members": party["members"],
            "creatures": party["creatures"],
            "usernames": party["usernames"],
            "host": party["host"],
            "state": party["state"],
            "timestamp": time.time()
        }
        
        # Send to all party members
        for member_id in party["members"]:
            if member_id in self.clients:
                member = self.clients[member_id]
                member.send(update)
                
    def broadcast_adventure_start(self, adventure_id):
        """
        Broadcast adventure start to all party members
        
        Parameters:
        -----------
        adventure_id : str
            ID of the adventure party
        """
        if adventure_id not in self.adventure_parties:
            return
            
        party = self.adventure_parties[adventure_id]
        
        # Create start message
        start = {
            "type": "ADVENTURE_START",
            "adventure_id": adventure_id,
            "members": party["members"],
            "creatures": party["creatures"],
            "usernames": party["usernames"],
            "host": party["host"],
            "timestamp": time.time()
        }
        
        # Send to all party members
        for member_id in party["members"]:
            if member_id in self.clients:
                member = self.clients[member_id]
                member.send(start)
                
        print(f"[Server] Adventure {adventure_id} started with {len(party['members'])} players")
        
    def get_adventure_parties(self):
        """
        Get list of active adventure parties
        
        Returns:
        --------
        list
            List of adventure party data
        """
        parties = []
        
        for party_id, party in self.adventure_parties.items():
            if party["state"] == "waiting":
                parties.append({
                    "id": party_id,
                    "host": party["host"],
                    "host_username": party["usernames"][0],
                    "member_count": len(party["members"]),
                    "creation_time": party["creation_time"]
                })
                
        return parties
