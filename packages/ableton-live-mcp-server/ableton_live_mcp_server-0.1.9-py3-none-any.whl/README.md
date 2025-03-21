# Ableton Live MCP Server

## 📌 Overview
The **Ableton Live MCP Server** is a server implementing the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) to facilitate communication between LLMs and **Ableton Live**. It uses **OSC (Open Sound Control)** to send and receive messages to/from Ableton Live.
It is based on [AbletonOSC](https://github.com/ideoforms/AbletonOSC) implementation and exhaustively maps available OSC adresses to [**tools**](https://modelcontextprotocol.io/docs/concepts/tools) accessible to MCP clients.


[![ontrol Ableton Live with LLMs](https://img.youtube.com/vi/12MzsQ3V7cs/hqdefault.jpg)](https://www.youtube.com/watch?v=12MzsQ3V7cs)

This project consists of two main components:
- `mcp_ableton_server.py`: The MCP server handling the communication between clients and the OSC daemon.
- `osc_daemon.py`: The OSC daemon responsible for relaying commands to Ableton Live and processing responses.

## ✨ Features
- Provides an MCP-compatible API for controlling Ableton Live from MCP clients.
- Uses **python-osc** for sending and receiving OSC messages.
- Based on the OSC implementation from [AbletonOSC](https://github.com/ideoforms/AbletonOSC).
- Implements request-response handling for Ableton Live commands.
- Supports working with Ableton devices and VST plugins, including browsing and controlling parameters.

## ⚡ Installation

### Option 1: Install with UV (Recommended)

1. Install UV if you don't have it already:
   ```bash
   pip install uv
   ```

2. Install directly from PyPI:
   ```bash
   uv install ableton-live-mcp-server
   ```

3. Or install from GitHub:
   ```bash
   uv install git+https://github.com/mrmos/ableton-live-mcp-server.git
   ```

### Option 2: Manual Installation

1. Install `uv`
   ```bash
   pip install uv
   ```
2. Clone the repository:
   ```bash
   git clone https://github.com/your-username/mcp_ableton_server.git
   cd mcp_ableton_server
   ```
3. Install dependencies:
   ```bash
   uv install python-osc fastmcp
   ```
4. Install the MCP Server
   This assumes that you're using [Claude Desktop](https://claude.ai/download)
   ```bash
   mcp install mcp_ableton_server.py
   ```
5. Install AbletonOSC
   Follow the instructions at [AbletonOSC](https://github.com/ideoforms/AbletonOSC)
   
## 🚀 Usage

### Running with a Single Command (Recommended)

The easiest way to start the Ableton Live MCP Server is with the included launcher script:

```bash
# Basic usage (runs both components with default settings)
ableton-mcp-start

# Show debug output from both components
ableton-mcp-start --debug

# Customize ports if needed
ableton-mcp-start --osc-port 65432 --mcp-port 8000 --ableton-port 11000 --receive-port 11001
```

The launcher automatically:
1. Starts the OSC daemon first
2. Verifies that it's running properly
3. Starts the MCP server
4. Monitors both processes and shuts them down gracefully on exit

### Manual Starting (Advanced)

Alternatively, you can manually start each component in separate terminal windows:

### Step 1: Run the OSC Daemon
First, start the OSC daemon to handle OSC communication between the MCP server and Ableton Live:
```bash
ableton-osc-daemon
```
This will:
- Listen for MCP client connections on port **65432**.
- Forward messages to Ableton Live via OSC on port **11000**.
- Receive OSC responses from Ableton on port **11001**.

### Step 2: Run the MCP Server
In a separate terminal window, start the MCP server to enable LLMs to control Ableton:
```bash
ableton-mcp-server
```

### Example Usage
In Claude desktop, ask Claude:
*Prepare a set to record a rock band*
*Set the input routing channel of all tracks that have "voice" in their name to Ext. In 2*

## Working with Devices and VST Plugins

The Ableton Live MCP Server provides tools to work with Ableton's devices and third-party VST plugins:

1. **Browse and Load Devices**: Browse Ableton's device library and load instruments or effects onto tracks.
2. **Get Device Information**: Retrieve detailed information about devices on tracks, including name, type, and parameters.
3. **Control Device Parameters**: Get and set parameter values for any device, including VST plugins.
4. **Browse VST Categories**: Navigate through Ableton's browser to find VST plugins.
5. **Browse and Load Presets**: Find and load presets for instruments and effects.

### Example Device and VST Usage

Here are some example prompts you can use with Claude:

- *Get all devices on track 1 and show me their parameters*
- *Set the filter cutoff parameter on the VST in track 3 to 0.7*
- *Browse available VST plugins and load Serum on a new MIDI track*
- *Show me all device parameters on the first track and set the filter cutoff to 120Hz*
- *Find all presets for Operator and load the "Bells" preset*
- *Browse presets for Serum and load one that sounds atmospheric*
- *Adjust the reverb on track 2 to be more dramatic*

Under the hood, the server uses AbletonOSC's device API to communicate with Ableton Live's devices:

- Device types are represented as: 1 = audio_effect, 2 = instrument, 4 = midi_effect
- External VST plugins are identified by their class_name (e.g., "PluginDevice", "AuPluginDevice")
- Parameters typically have normalized values between 0.0 and 1.0
- The browser API is used to locate and load VST plugins and presets

## ⚙️ Configuration
By default, the server and daemon run on **localhost (127.0.0.1)** with the following ports:
- **MCP Server Socket:** 65432
- **Ableton Live OSC Port (Send):** 11000
- **Ableton Live OSC Port (Receive):** 11001

To modify these, edit the `AbletonOSCDaemon` class in `osc_daemon.py` or use command-line parameters:
```bash
ableton-osc-daemon --socket-port 65432 --ableton-port 11000 --receive-port 11001
```

### Claude Desktop Configuration

To configure Claude Desktop to use Ableton Live MCP Server:

1. Edit the Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`

2. Add the following to your configuration:

```json
"mcpServers": {
  "Ableton Live Controller": {
    "command": "ableton-mcp-start",
    "args": []
  }
}
```

3. For debugging with visible output:

```json
"mcpServers": {
  "Ableton Live Controller": {
    "command": "ableton-mcp-start",
    "args": ["--debug"]
  }
}
```

4. Restart Claude Desktop

## Contributing
Feel free to submit issues, feature requests, or pull requests to improve this project.

## Publishing Updates
To publish new versions using UV:

1. Update the version in `pyproject.toml`
2. Build the package:
   ```bash
   uv build
   ```
3. Publish to PyPI:
   ```bash
   uv publish
   ```

## License
This project is licensed under the **MIT License**. See the `LICENSE` file for details.

## Acknowledgments
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [python-osc](https://github.com/attwad/python-osc) for OSC handling
- Daniel John Jones for OSC implementation with [AbletonOSC](https://github.com/ideoforms/AbletonOSC)
- Ableton Third Party Remote Scripts
- Julien Bayle @[Structure Void](https://structure-void.com/) for endless inspirations and resources.

## TODO
- Explore *resources* and *prompts* primitives opportunities.
- Build a standalone Ableton Live MCP client.

---

