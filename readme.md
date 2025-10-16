# System Info Textual TUI

A comprehensive real-time system monitoring tool built with Python and Textual. Monitor your GPU, network interfaces, and Docker containers all in one beautiful terminal user interface.

![System Monitor](https://img.shields.io/badge/Platform-Linux-blue) ![Python](https://img.shields.io/badge/Python-3.8+-brightgreen) ![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

### 🖥️ **GPU Monitoring**
- Real-time GPU statistics via `nvidia-smi`
- GPU temperature, memory usage, and utilization with **graphical progress bars**
- Color-coded indicators (🟢 Green: Safe, 🟡 Yellow: Medium, 🔴 Red: High)
- GPU model and board information
- Live monitoring of GPU processes with PID, process name, and memory usage
- Multi-GPU support with easy switching

### 🌐 **Network Statistics**
- Real-time network interface monitoring
- Automatic detection of Ethernet, WiFi, and other interface types
- IP address display with CIDR notation and scope information
- Network traffic statistics (RX/TX in MB/GB)
- Interface status monitoring (UP/DOWN)
- Error count tracking
- Cycle through multiple network interfaces

### 🐳 **Docker Container Management**
- Live Docker container monitoring via `docker ps -a`
- Container status (running/stopped/exited) with visual indicators
- CPU and memory usage for running containers
- Container image and port information
- Real-time container statistics

### 🎨 **Visual Features**
- Clean bordered panels with thin ASCII borders
- Color-coded status indicators and progress bars
- Real-time updates with configurable refresh intervals
- Intuitive keyboard navigation
- Professional dark theme with syntax highlighting

## Requirements

### System Requirements
- **Operating System**: Linux (tested on Ubuntu/Debian)
- **Python**: 3.8 or higher
- **GPU**: NVIDIA GPU with nvidia-smi installed (for GPU monitoring)
- **Docker**: Docker installed and accessible (for container monitoring)

### Dependencies
- `textual` - Modern TUI framework
- `subprocess` - System command execution (built-in)
- `re` - Regular expressions (built-in)
- `json` - JSON parsing (built-in)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/system-info-textual-tui.git
cd system-info-textual-tui
```

### 2. Create Virtual Environment (Recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/macOS
```

### 3. Install Dependencies

```bash
pip install textual
```

```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
pip install -r requirements.txt
```

### 4. Install System Dependencies

#### NVIDIA GPU Support
```bash
# Install NVIDIA drivers and nvidia-smi
sudo apt update
sudo apt install nvidia-driver-xxx nvidia-utils-xxx
```

#### Docker Support (Optional)
```bash
# Install Docker
sudo apt install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER  # Add user to docker group
```

## Usage

### Basic Usage
```bash
# Navigate to the project directory
cd system-info-textual-tui

# Activate virtual environment
source .venv/bin/activate

# Run the application
python3 system-info-textual-tui.py
```

### Run in the Browser

```bash
textual serve python3 system-info-textual-tui.py
```
Then load up http://localhost:8080 to see the Browser goodness.


### Keyboard Controls

| Key | Action | Description |
|-----|--------|-------------|
| `q` | Quit | Exit the application |
| `g` | Next GPU | Switch to next GPU (multi-GPU systems) |
| `G` | Previous GPU | Switch to previous GPU |
| `n` | Next Interface | Cycle to next network interface |
| `N` | Previous Interface | Cycle to previous network interface |
| `d` | Toggle Docker | Toggle Docker container display |
| `Ctrl+p` | Palette | Open command palette |

### Understanding the Display

#### GPU Statistics Panel
```
┌─ 🖥️  GPU Statistics ────────────────────────────────┐
│ GPU ID: 0                                          │
│ Model: NVIDIA GeForce RTX 4090                     │
│                                                    │
│ Temperature: ████████░░░░░░░ 🟢 45.2% (67°C)       │
│ Memory: ██████████████░░░░░ 🟡 73.2% (18432/24576MB) │
│ Utilization: ███░░░░░░░░░░░ 🟢 15.0% (15%)         │
│                                                    │
│ Running Processes:                                 │
│   PID: 12345 | python | Mem: 2048 MB              │
└────────────────────────────────────────────────────┘
```

#### Network Statistics Panel
```
┌─ 🌐 Network Statistics ─────────────────────────────┐
│ Interface: wlan0                                   │
│ Type: WiFi                                         │
│ Status: UP                                         │
│ IP Addresses:                                      │
│   192.168.1.100/24 (Global)                       │
│                                                    │
│ Traffic Statistics:                                │
│   RX (Received): 1.25 GB                          │
│   TX (Transmitted): 847.3 MB                       │
│   RX Errors: 0                                     │
└────────────────────────────────────────────────────┘
```

## Configuration

### Refresh Intervals
The application uses different refresh intervals for different components:

- **GPU Statistics**: 5 seconds
- **Network Statistics**: 5 seconds  
- **Docker Containers**: 10 seconds
- **Log Panel**: 2 seconds

### Customization
You can modify the refresh intervals and other settings by editing the respective `set_interval()` calls in the source code.

## Troubleshooting

### Common Issues

#### GPU Not Detected
```
Error: No GPU detected or nvidia-smi not available
```
**Solution**: 
- Ensure NVIDIA drivers are installed: `nvidia-smi`
- Check if GPU is properly connected
- Install nvidia-utils package

#### Network Interface Shows N/A
```
IP Address: N/A
Status: DOWN
```
**Solution**:
- Check if interface is up: `ip link show`
- Ensure interface has IP assigned: `ip addr show`
- Try different interface with `n` key

#### Docker Errors
```
Docker error: docker: command not found
```
**Solution**:
- Install Docker: `sudo apt install docker.io`
- Start Docker service: `sudo systemctl start docker`
- Add user to docker group: `sudo usermod -aG docker $USER`

#### Permission Issues
```
Permission denied
```
**Solution**:
- Run with appropriate permissions for system commands
- Ensure user is in docker group for Docker commands
- Some network information may require elevated privileges

### Debug Mode
For debugging issues, you can run individual system commands manually:

```bash
# Test GPU detection
nvidia-smi --query-gpu=name,temperature.gpu,memory.used --format=csv

# Test network interfaces  
ip addr show

# Test Docker
docker ps -a --format json
```

## Development

### Project Structure
```
system-info-textual-tui/
├── system-info-textual-tui.py   # Main application file
├── styles.css                   # Textual CSS styling
├── requirements.txt             # Python dependencies
├── readme.md                    # This file
├── tmux-command-window.sh       # Tmux helper script
├── docs/                        # Documentation
└── .venv/                       # Virtual environment
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Textual](https://github.com/Textualize/textual) - Modern Python TUI framework
- Uses NVIDIA's `nvidia-smi` for GPU monitoring
- Network monitoring via Linux `ip` commands
- Docker integration via Docker CLI

---

**Note**: This application requires a Linux environment with appropriate system tools installed.

