from mcp.server.fastmcp import FastMCP
import asyncio
import json
import socket
import sys
from typing import List, Optional


# Define version
__version__ = "0.1.6"

class AbletonClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.responses = {}  # Store futures keyed by (request_id)
        self.lock = asyncio.Lock()
        self._request_id = 0  # compteur pour générer des ids uniques
        
        # Task asynchrone pour lire les réponses
        self.response_task = None

    async def start_response_reader(self):
        """Background task to read responses from the socket, potentially multiple messages."""
        # On convertit self.sock en Streams asyncio
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        loop = asyncio.get_running_loop()
        await loop.create_connection(lambda: protocol, sock=self.sock)

        while self.connected:
            try:
                data = await reader.read(4096)
                if not data:
                    # Connection close
                    break

                try:
                    msg = json.loads(data.decode())
                except json.JSONDecodeError:
                    print("Invalid JSON from daemon", file=sys.stderr)
                    continue

                # Si c'est une réponse JSON-RPC
                resp_id = msg.get('id')
                if 'result' in msg or 'error' in msg:
                    # Réponse à une requête
                    async with self.lock:
                        fut = self.responses.pop(resp_id, None)
                    if fut and not fut.done():
                        fut.set_result(msg)
                else:
                    # Sinon c'est un message "osc_response" ou un autre type
                    # (Selon le code du daemon)
                    if msg.get('type') == 'osc_response':
                        # On peut router selon l'adresse
                        address = msg.get('address')
                        args = msg.get('args')
                        await self.handle_osc_response(address, args)
                    else:
                        print(f"Unknown message: {msg}", file=sys.stderr)

            except Exception as e:
                print(f"Error reading response: {e}", file=sys.stderr)
                break

    async def handle_osc_response(self, address: str, args):
        """Callback quand on reçoit un message de type OSC depuis Ableton."""
        # Exemple simple : on pourrait faire un set_result sur un future
        print(f"OSC Notification from {address}: {args}", file=sys.stderr)

    async def connect(self):
        """Connect to the OSC daemon via TCP socket."""
        if not self.connected:
            try:
                self.sock.connect((self.host, self.port))
                self.connected = True
                
                # Now this is properly awaited
                self.response_task = asyncio.create_task(self.start_response_reader())
                print(f"Connected to OSC daemon at {self.host}:{self.port}")
                return True
            except Exception as e:
                print(f"Failed to connect to daemon: {e}", file=sys.stderr)
                print("Make sure the OSC daemon is running with: ableton-osc-daemon")
                return False
        return True

    async def send_rpc_request(self, method: str, params: dict) -> dict:
        """
        Envoie une requête JSON-RPC (method, params) et attend la réponse.
        """
        if not self.connected:
            # Properly await the connect method
            if not await self.connect():
                return {'status': 'error', 'message': 'Not connected to daemon'}

        # Génération d'un ID unique
        self._request_id += 1
        request_id = str(self._request_id)

        # Construit la requête JSON-RPC
        request_obj = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }

        future = asyncio.Future()
        async with self.lock:
            self.responses[request_id] = future

        try:
            self.sock.sendall(json.dumps(request_obj).encode())

            # Attend la réponse JSON-RPC
            try:
                msg = await asyncio.wait_for(future, timeout=5.0)
            except asyncio.TimeoutError:
                async with self.lock:
                    self.responses.pop(request_id, None)
                return {'status': 'error', 'message': 'Response timeout'}

            # On check si on a un 'result' ou un 'error'
            if 'error' in msg:
                return {
                    'status': 'error',
                    'code': msg['error'].get('code'),
                    'message': msg['error'].get('message')
                }
            else:
                return {
                    'status': 'ok',
                    'result': msg.get('result')
                }

        except Exception as e:
            self.connected = False
            return {'status': 'error', 'message': str(e)}
    """
    def send_rpc_command_sync(self, method: str, params: dict) -> dict:
        
        # Variante synchrone pour juste envoyer le message
        # et lire UNE réponse immédiatement (fonctionne si
        # le daemon renvoie une unique réponse).
        
        if not self.connected:
            if not self.connect():
                return {'status': 'error', 'message': 'Not connected'}

        # On envoie un ID, etc.
        self._request_id += 1
        request_id = str(self._request_id)

        request_obj = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }
        try:
            self.sock.sendall(json.dumps(request_obj).encode())
            resp_data = self.sock.recv(4096)
            if not resp_data:
                return {'status': 'error', 'message': 'No response'}

            msg = json.loads(resp_data.decode())
            if 'error' in msg:
                return {
                    'status': 'error',
                    'code': msg['error'].get('code'),
                    'message': msg['error'].get('message')
                }
            else:
                return {'status': 'ok', 'result': msg.get('result')}

        except Exception as e:
            self.connected = False
            return {'status': 'error', 'message': str(e)}
    """
    async def close(self):
        """Close the connection."""
        if self.connected:
            self.connected = False
            if self.response_task:
                self.response_task.cancel()
                try:
                    await self.response_task
                except asyncio.CancelledError:
                    pass
            self.sock.close()


# Initialize the MCP server
mcp = FastMCP("Ableton Live Controller", dependencies=["python-osc"])

# Create Ableton client
ableton_client = AbletonClient()


# MCP Server configuration

@mcp.tool()
async def get_session_info(random_string: str) -> str:
    """Get detailed information about the current Ableton session"""
    response = await ableton_client.send_osc('/live/song/get_info', [])
    return json.dumps(response)

@mcp.tool()
async def get_track_info(track_index: int) -> str:
    """
    Get detailed information about a specific track in Ableton.
    
    Parameters:
    - track_index: The index of the track to get information about
    """
    response = await ableton_client.send_osc('/live/track/get_info', [track_index])
    return json.dumps(response)

# ----- TOOLS WITH RESPONSE -----

@mcp.tool()
async def get_track_names(index_min: Optional[int] = None, index_max: Optional[int] = None) -> str:
    """
    Get the names of tracks in Ableton Live.
    
    Args:
        index_min: Optional minimum track index
        index_max: Optional maximum track index
    
    Returns:
        A formatted string containing track names
    """
    params = {}
    if index_min is not None and index_max is not None:
        params["address"] = "/live/song/get/track_names"
        params["args"] = [index_min, index_max]
    else:
        params["address"] = "/live/song/get/track_names"
        params["args"] = []

    response = await ableton_client.send_rpc_request("send_message", params)
    if response['status'] == 'ok':
        track_names = response['result'].get('status')
        # Ici, j'ai mis 'status' car dans le daemon, on renvoie "result": {"status":"sent"} ou autre
        # Mais si vous modifiez le daemon pour retourner vraiment les noms de pistes, changez la structure correspondante.
        if not track_names:
            return "No tracks found"
        # Supposons qu'on reçoive un tableau de noms => adapter en conséquence
        # track_names = ["Track1", "Track2", ...]
        # ...
        return f"Track Names: {track_names}"
    else:
        return f"Error getting track names: {response.get('message', 'Unknown error')}"

@mcp.tool()
async def create_midi_track(index: int = -1) -> str:
    """
    Create a new MIDI track in the Ableton session.
    
    Parameters:
    - index: The index to insert the track at (-1 = end of list)
    """
    response = await ableton_client.send_osc('/live/song/create_midi_track', [index])
    return json.dumps(response)

@mcp.tool()
async def set_track_name(track_index: int, name: str) -> str:
    """
    Set the name of a track.
    
    Parameters:
    - track_index: The index of the track to rename
    - name: The new name for the track
    """
    response = await ableton_client.send_osc('/live/track/set_name', [track_index, name])
    return json.dumps(response)

@mcp.tool()
async def create_clip(track_index: int, clip_index: int, length: float = 4.0) -> str:
    """
    Create a new MIDI clip in the specified track and clip slot. First check if there are less than 7 clips, if not, ask the user to delete a clip first.
    
    Parameters:
    - track_index: The index of the track to create the clip in
    - clip_index: The index of the clip slot to create the clip in
    - length: The length of the clip in beats (default: 4.0)
    """
    response = await ableton_client.send_osc('/live/clip/create', [track_index, clip_index, length])
    return json.dumps(response)

@mcp.tool()
async def add_notes_to_clip(track_index: int, clip_index: int, notes: List[dict]) -> str:
    """
    Add MIDI notes to a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - notes: List of note dictionaries, each with pitch, start_time, duration, velocity, and mute
    """
    # Flatten the notes array for OSC
    notes_flat = []
    for note in notes:
        notes_flat.extend([
            note.get("pitch", 60),
            note.get("start_time", 0.0),
            note.get("duration", 1.0),
            note.get("velocity", 100),
            1 if note.get("mute", False) else 0
        ])
    
    response = await ableton_client.send_osc('/live/clip/add_notes', [track_index, clip_index, *notes_flat])
    return json.dumps(response)

@mcp.tool()
async def set_clip_name(track_index: int, clip_index: int, name: str) -> str:
    """
    Set the name of a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - name: The new name for the clip
    """
    response = await ableton_client.send_osc('/live/clip/set_name', [track_index, clip_index, name])
    return json.dumps(response)

@mcp.tool()
async def set_tempo(tempo: float) -> str:
    """
    Set the tempo of the Ableton session.
    
    Parameters:
    - tempo: The new tempo in BPM
    """
    response = await ableton_client.send_osc('/live/song/set_tempo', [tempo])
    return json.dumps(response)

@mcp.tool()
async def load_instrument_or_effect(track_index: int, uri: str) -> str:
    """
    Load an instrument or effect onto a track using its URI.
    
    Parameters:
    - track_index: The index of the track to load the instrument on
    - uri: The URI of the instrument or effect to load (e.g., 'query:Synths#Instrument%20Rack:Bass:FileId_5116')
    """
    response = await ableton_client.send_osc('/live/track/load_device', [track_index, uri])
    return json.dumps(response)

@mcp.tool()
async def fire_clip(track_index: int, clip_index: int) -> str:
    """
    Start playing a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    response = await ableton_client.send_osc('/live/clip/fire', [track_index, clip_index])
    return json.dumps(response)

@mcp.tool()
async def stop_clip(track_index: int, clip_index: int) -> str:
    """
    Stop playing a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    response = await ableton_client.send_osc('/live/clip/stop', [track_index, clip_index])
    return json.dumps(response)

@mcp.tool()
async def start_playback(random_string: str) -> str:
    """Start playing the Ableton session."""
    response = await ableton_client.send_osc('/live/song/start_playing', [])
    return json.dumps(response)

@mcp.tool()
async def stop_playback(random_string: str) -> str:
    """Stop playing the Ableton session."""
    response = await ableton_client.send_osc('/live/song/stop_playing', [])
    return json.dumps(response)

@mcp.tool()
async def get_browser_tree(category_type: str = "all") -> str:
    """
    Get a hierarchical tree of browser categories from Ableton.
    
    Parameters:
    - category_type: Type of categories to get ('all', 'instruments', 'sounds', 'drums', 'audio_effects', 'midi_effects')
    """
    response = await ableton_client.send_osc('/live/browser/get_tree', [category_type])
    return json.dumps(response)

@mcp.tool()
async def get_browser_items_at_path(path: str) -> str:
    """
    Get browser items at a specific path in Ableton's browser.
    
    Parameters:
    - path: Path in the format "category/folder/subfolder"
            where category is one of the available browser categories in Ableton
    """
    response = await ableton_client.send_osc('/live/browser/get_items_at_path', [path])
    return json.dumps(response)

@mcp.tool()
async def load_drum_kit(track_index: int, rack_uri: str, kit_path: str) -> str:
    """
    Load a drum rack and then load a specific drum kit into it.
    
    Parameters:
    - track_index: The index of the track to load on
    - rack_uri: The URI of the drum rack to load (e.g., 'Drums/Drum Rack')
    - kit_path: Path to the drum kit inside the browser (e.g., 'drums/acoustic/kit1')
    """
    # First load the drum rack
    rack_response = await ableton_client.send_osc('/live/track/load_device', [track_index, rack_uri])
    
    # Then load the kit
    kit_response = await ableton_client.send_osc('/live/browser/load_drum_kit', [track_index, kit_path])
    
    return json.dumps({
        "rack_response": rack_response,
        "kit_response": kit_response
    })

def main():
    """Entry point for the MCP server when run as a command-line application."""
    import os
    import uvicorn
    from mcp.server.fastmcp import FastMCP
    
    # We need to run the connect method asynchronously
    async def async_connect():
        if not await ableton_client.connect():
            print("ERROR: Cannot connect to the OSC daemon.")
            print("Please start the OSC daemon first with: ableton-osc-daemon")
            print("For more information, see the documentation.")
            return False
        return True
    
    # Run the connect method in a new event loop
    try:
        connect_result = asyncio.run(async_connect())
        if not connect_result:
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to connect to OSC daemon: {e}")
        print("Please start the OSC daemon first with: ableton-osc-daemon")
        sys.exit(1)
    
    # Get all available tools
    tools = []
    all_functions = globals()
    for name, obj in all_functions.items():
        if callable(obj) and hasattr(obj, '__mcp_tool__'):
            tools.append(obj)
        elif callable(obj) and hasattr(obj, '_fastmcp_tool'):
            tools.append(obj)
    
    if not tools:
        print("WARNING: No MCP tools found. The server may not function correctly.")
    else:
        print(f"Found {len(tools)} MCP tools.")
        
    # List all the tools found
    for t in tools:
        print(f"  - {t.__name__}")
    
    # Configure the FastMCP server
    app = FastMCP(
        name="Ableton Live MCP Server",
        tools=tools,
        prefix="mcp_AbletonMCP_"
    )
    
    # Start the FastMCP server
    port = int(os.environ.get("MCP_PORT", 8000))
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    
    print(f"Starting Ableton Live MCP Server on {host}:{port}")
    print("Press Ctrl+C to exit")
    
    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        print("Shutting down MCP server...")
    finally:
        asyncio.run(ableton_client.close())

if __name__ == "__main__":
    main()