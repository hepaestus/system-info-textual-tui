
import textual
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Header, Footer, Log, DataTable
from textual.reactive import reactive
from textual import events
import subprocess
import time
import threading
import re
import json
import webbrowser
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# SYMBOL CONSTANTS - Customize the visual symbols used throughout the interface
# ═══════════════════════════════════════════════════════════════════════════════

class Symbols:
    # Progress bar symbols
    PROGRESS_FILLED = "█"      # Filled portion of progress bars
    PROGRESS_EMPTY = "░"       # Empty portion of progress bars
    PROGRESS_MEDIUM = "▒"      # Medium fill (used in network graph)
    
    # Status indicators
    STATUS_HIGH = "🔴"         # High usage/critical status (red circle)
    STATUS_MEDIUM = "🟡"       # Medium usage/warning status (yellow circle)
    STATUS_LOW = "🟢"          # Low usage/good status (green circle)
    
    # Panel title icons
    GPU_ICON = "🖥️"           # GPU panel title
    NETWORK_ICON = "🌐"        # Network panel title
    GRAPH_ICON = "📊"          # Graph panel title
    DOCKER_ICON = "🐳"         # Docker panel title
    LOG_ICON = "📋"            # Log panel title
    
    # Header icons
    CALENDAR_ICON = "📅"       # Date display
    CLOCK_ICON = "🕐"          # Time display
    
    # Network interface icons
    ETHERNET_ICON = "🌐"       # Ethernet interface
    WIFI_ICON = "📶"           # WiFi interface
    IP_ICON = "📍"             # IP address indicator
    TRAFFIC_ICON = "📊"        # Traffic statistics
    TOTAL_ICON = "📈"          # Total traffic
    
    # Docker status icons
    CONTAINER_RUNNING = "📦"   # Running container
    CONTAINER_STOPPED = "⏹️"   # Stopped container
    CONTAINER_ERROR = "❌"     # Container error/exited
    
    # General status icons
    ERROR_ICON = "❌"          # Error indicator
    NO_DATA_ICON = "❌"        # No data available
    
    # Box drawing characters (for graphs)
    BOX_TOP_LEFT = "┌"         # Top-left corner
    BOX_TOP_RIGHT = "┐"        # Top-right corner
    BOX_BOTTOM_LEFT = "└"      # Bottom-left corner
    BOX_BOTTOM_RIGHT = "┘"     # Bottom-right corner
    BOX_HORIZONTAL = "─"       # Horizontal line
    BOX_VERTICAL = "│"         # Vertical line
    
    # Traffic direction arrows
    DOWNLOAD_ARROW = "↓"       # Download traffic
    UPLOAD_ARROW = "↑"         # Upload traffic

class Colors:

    # Progress bar colors (Textual rich markup)
    PROGRESS_HIGH = "red"      # High usage progress bars (80%+)
    PROGRESS_MEDIUM = "yellow" # Medium usage progress bars (60-80%)
    PROGRESS_LOW = "green"     # Low usage progress bars (0-60%)
    PROGRESS_BACKGROUND = "grey37"  # Empty/background portion
    
    # Alternative color schemes (uncomment to use)
    # Modern theme
    # PROGRESS_HIGH = "bright_red"
    # PROGRESS_MEDIUM = "orange1" 
    # PROGRESS_LOW = "bright_green"
    # PROGRESS_BACKGROUND = "grey37"
    
    # Cyberpunk theme
    # PROGRESS_HIGH = "magenta"
    # PROGRESS_MEDIUM = "cyan"
    # PROGRESS_LOW = "bright_green"
    # PROGRESS_BACKGROUND = "grey11"
    
    # Thermal theme (for temperature bars)
    TEMP_CRITICAL = "bright_red"    # 80°C+
    TEMP_WARNING = "orange1"        # 60-80°C  
    TEMP_NORMAL = "bright_blue"     # <60°C
    
    # Memory usage colors
    MEM_CRITICAL = "bright_red"     # 90%+ memory usage
    MEM_HIGH = "red"                # 70-90% memory usage
    MEM_MEDIUM = "yellow"           # 50-70% memory usage
    MEM_LOW = "green"               # <50% memory usage
    
    # Network activity colors
    NET_HIGH_ACTIVITY = "bright_green"   # High network throughput
    NET_MED_ACTIVITY = "yellow"          # Medium network throughput  
    NET_LOW_ACTIVITY = "dim cyan"        # Low network throughput
    
    # Text colors
    TEXT_PRIMARY = "white"          # Primary text
    TEXT_SECONDARY = "grey70"       # Secondary/dim text
    TEXT_SUCCESS = "green"          # Success messages
    TEXT_WARNING = "yellow"         # Warning messages
    TEXT_ERROR = "red"              # Error messages
    
    # Header icons
    CALENDAR_ICON = "📅"       # Date display
    CLOCK_ICON = "🕐"          # Time display
    
    # Network interface icons
    ETHERNET_ICON = "🌐"       # Ethernet interface
    WIFI_ICON = "📶"           # WiFi interface
    IP_ICON = "📍"             # IP address indicator
    TRAFFIC_ICON = "📊"        # Traffic statistics
    TOTAL_ICON = "📈"          # Total traffic
    
    # Docker status icons
    CONTAINER_RUNNING = "📦"   # Running container
    CONTAINER_STOPPED = "⏹️"   # Stopped container
    CONTAINER_ERROR = "❌"     # Container error/exited
    
    # General status icons
    ERROR_ICON = "❌"          # Error indicator
    NO_DATA_ICON = "❌"        # No data available
    
    # Box drawing characters (for graphs)
    BOX_TOP_LEFT = "┌"         # Top-left corner
    BOX_TOP_RIGHT = "┐"        # Top-right corner
    BOX_BOTTOM_LEFT = "└"      # Bottom-left corner
    BOX_BOTTOM_RIGHT = "┘"     # Bottom-right corner
    BOX_HORIZONTAL = "─"       # Horizontal line
    BOX_VERTICAL = "│"         # Vertical line
    
    # Traffic direction arrows
    DOWNLOAD_ARROW = "↓"       # Download traffic
    UPLOAD_ARROW = "↑"         # Upload traffic

class GPUProcessTable(DataTable):
    """DataTable widget for displaying GPU processes"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = f"{Symbols.GPU_ICON} GPU Processes"
        self.zebra_stripes = True
        self.cursor_type = "row"
        self.show_header = True
        
    def on_mount(self):
        # Add columns
        self.add_column("PID", width=8)
        self.add_column("Process Name", width=30)
        self.add_column("Memory", width=12)
    
    def update_processes(self, processes):
        """Update the table with new process data"""
        # Clear existing rows
        self.clear()
        
        if not processes:
            self.add_row("No processes", "running on GPU", "-")
            return
            
        # Sort processes by memory usage (descending)
        sorted_processes = sorted(processes, 
                                key=lambda x: self._extract_memory_mb(x.get('Memory', '0 MB')), 
                                reverse=True)
        
        for proc in sorted_processes:
            pid = proc.get('PID', 'N/A')
            name = proc.get('Name', 'Unknown Process')
            memory = proc.get('Memory', 'N/A MB')
            
            # Truncate long process names (increased width since we removed Type column)
            if len(name) > 27:
                name = name[:24] + "..."
                
            self.add_row(pid, name, memory)
    
    def _extract_memory_mb(self, memory_str):
        """Extract memory value in MB for sorting purposes"""
        try:
            match = re.search(r'(\d+)', memory_str)
            if match:
                return int(match.group(1))
            return 0
        except (ValueError, AttributeError):
            return 0

class GPUStats(Static):
    gpu_id = reactive(0)
    gpu_data = reactive({})
    running_processes = reactive([])

    def on_mount(self):
        self.update_gpu_data()
        self.set_interval(5, self.update_gpu_data)

    def update_gpu_data(self):
        try:
            # Get GPU info using nvidia-smi
            cmd = ["nvidia-smi", "--query-gpu=index,name,temperature.gpu,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                if self.gpu_id < len(lines):
                    parts = [part.strip() for part in lines[self.gpu_id].split(',')]
                    if len(parts) >= 6:
                        gpu_index, gpu_name, temp, mem_used, mem_total, util = parts
                        self.gpu_data = {
                            "GPU ID": gpu_index,
                            "Model": gpu_name,
                            "Temperature": f"{temp} °C",
                            "Memory Usage": f"{mem_used} MB / {mem_total} MB",
                            "Utilization": f"{util} %",
                        }
                    else:
                        raise ValueError("Invalid nvidia-smi output format")
                else:
                    # GPU ID not found, use first available GPU
                    self.gpu_id = 0
                    if lines:
                        parts = [part.strip() for part in lines[0].split(',')]
                        if len(parts) >= 6:
                            gpu_index, gpu_name, temp, mem_used, mem_total, util = parts
                            self.gpu_data = {
                                "GPU ID": gpu_index,
                                "Model": gpu_name,
                                "Temperature": f"{temp} °C",
                                "Memory Usage": f"{mem_used} MB / {mem_total} MB",
                                "Utilization": f"{util} %",
                            }
            else:
                raise subprocess.CalledProcessError(result.returncode, cmd)
                
            # Get running processes on GPU using nvidia-smi -q
            proc_cmd = ["nvidia-smi", "-q"]
            proc_result = subprocess.run(proc_cmd, capture_output=True, text=True, timeout=10)
            
            self.running_processes = []
            if proc_result.returncode == 0 and proc_result.stdout.strip():
                lines = proc_result.stdout.strip().split('\n')
                current_gpu = None
                in_processes_section = False
                current_process = {}
                
                for line in lines:
                    line = line.strip()
                    
                    # Track which GPU we're looking at
                    if line.startswith("GPU "):
                        gpu_match = re.search(r'GPU (\d+)', line)
                        if gpu_match:
                            current_gpu = int(gpu_match.group(1))
                            in_processes_section = False
                    
                    # Only process data for the current GPU
                    if current_gpu == self.gpu_id:
                        if line == "Processes":
                            in_processes_section = True
                            continue
                        
                        if in_processes_section:
                            if line.startswith("Process ID"):
                                pid_match = re.search(r'Process ID\s*:\s*(\d+)', line)
                                if pid_match:
                                    if current_process:  # Save previous process if exists
                                        self.running_processes.append(current_process)
                                    current_process = {"PID": pid_match.group(1)}
                            
                            elif line.startswith("Name") and "PID" in current_process:
                                name_match = re.search(r'Name\s*:\s*(.+)', line)
                                if name_match:
                                    current_process["Name"] = name_match.group(1).strip()
                            
                            elif line.startswith("Used GPU Memory") and "PID" in current_process:
                                mem_match = re.search(r'Used GPU Memory\s*:\s*(\d+)\s*MiB', line)
                                if mem_match:
                                    current_process["Memory"] = f"{mem_match.group(1)} MB"
                
                # Don't forget the last process
                if current_process and "PID" in current_process:
                    self.running_processes.append(current_process)
                
                # Ensure all processes have required fields
                for proc in self.running_processes:
                    if "Name" not in proc:
                        proc["Name"] = "Unknown Process"
                    if "Memory" not in proc:
                        proc["Memory"] = "N/A MB"
                        
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, FileNotFoundError) as e:
            # Fallback if nvidia-smi is not available or fails
            self.gpu_data = {
                "GPU ID": self.gpu_id,
                "Model": "No GPU detected or nvidia-smi not available",
                "Temperature": "N/A",
                "Memory Usage": "N/A",
                "Utilization": "N/A",
                "Error": str(e)
            }
            self.running_processes = []
        
        # Update the process table if it exists
        self._update_process_table()
        self.refresh()
    
    def _update_process_table(self):
        """Update the GPU process table through the app"""
        try:
            # Get the app instance and update the process table
            app = self.app
            if hasattr(app, 'gpu_process_table'):
                app.gpu_process_table.update_processes(self.running_processes)
        except Exception:
            # If we can't update the table, that's okay
            pass

    def _extract_memory_mb(self, memory_str):
        """Extract memory value in MB for sorting purposes"""
        try:
            # Extract number from strings like "123 MB", "N/A MB", etc.
            match = re.search(r'(\d+)', memory_str)
            if match:
                return int(match.group(1))
            return 0
        except (ValueError, AttributeError):
            return 0

    def create_progress_bar(self, value, max_value, width=30, label="", bar_type="generic"):
        """Create a text-based progress bar with color support"""
        if value == "N/A" or max_value == "N/A":
            return f"{label}: N/A"
        
        try:
            percentage = min(float(value) / float(max_value), 1.0)
            filled = int(percentage * width)
            
            # Choose colors based on bar type and percentage
            if bar_type == "temperature":
                if percentage >= 0.89:  # 80°C+ for 90°C max
                    fill_color = Colors.TEMP_CRITICAL
                    status_icon = Symbols.STATUS_HIGH
                elif percentage >= 0.67:  # 60°C+ for 90°C max
                    fill_color = Colors.TEMP_WARNING
                    status_icon = Symbols.STATUS_MEDIUM
                else:
                    fill_color = Colors.TEMP_NORMAL
                    status_icon = Symbols.STATUS_LOW
            elif bar_type == "memory":
                if percentage >= 0.9:
                    fill_color = Colors.MEM_CRITICAL
                    status_icon = Symbols.STATUS_HIGH
                elif percentage >= 0.7:
                    fill_color = Colors.MEM_HIGH
                    status_icon = Symbols.STATUS_HIGH
                elif percentage >= 0.5:
                    fill_color = Colors.MEM_MEDIUM
                    status_icon = Symbols.STATUS_MEDIUM
                else:
                    fill_color = Colors.MEM_LOW
                    status_icon = Symbols.STATUS_LOW
            else:  # Generic progress bar
                if percentage >= 0.8:
                    fill_color = Colors.PROGRESS_HIGH
                    status_icon = Symbols.STATUS_HIGH
                elif percentage >= 0.6:
                    fill_color = Colors.PROGRESS_MEDIUM
                    status_icon = Symbols.STATUS_MEDIUM
                else:
                    fill_color = Colors.PROGRESS_LOW
                    status_icon = Symbols.STATUS_LOW
            
            # Create colored progress bar using Textual rich markup
            filled_bar = f"[{fill_color}]{Symbols.PROGRESS_FILLED * filled}[/{fill_color}]"
            empty_bar = f"[{Colors.PROGRESS_BACKGROUND}]{Symbols.PROGRESS_EMPTY * (width - filled)}[/{Colors.PROGRESS_BACKGROUND}]"
            bar = filled_bar + empty_bar
            
            return f"{label}: {bar} {status_icon} {percentage*100:.1f}%"
        except (ValueError, ZeroDivisionError):
            return f"{label}: N/A"

    def render(self):
        lines = [f"GPU Stats (GPU {self.gpu_id}):"]
        
        # Calculate available width for progress bars (account for borders, labels, and extra info)
        # Use getattr with fallback for cases where size isn't available yet
        widget_width = getattr(self.size, 'width', 80) if hasattr(self, 'size') else 80
        available_width = max(widget_width - 35, 15)  # Reserve space for labels and values, minimum 15
        bar_width = min(available_width, 30)  # Cap at reasonable maximum
        
        # Display GPU ID and Model first
        if "GPU ID" in self.gpu_data:
            lines.append(f"GPU ID: {self.gpu_data['GPU ID']}")
        if "Model" in self.gpu_data:
            lines.append(f"Model: {self.gpu_data['Model']}")
        
        # Temperature with graphical representation
        if "Temperature" in self.gpu_data and self.gpu_data["Temperature"] != "N/A":
            temp_str = self.gpu_data["Temperature"].replace(" °C", "")
            try:
                temp_val = float(temp_str)
                temp_bar = self.create_progress_bar(temp_val, 90, bar_width, "Temperature".ljust(11), "temperature")  # Max temp 90°C
                lines.append(f"{temp_bar} ({temp_val}°C)")
            except ValueError:
                lines.append(f"Temperature: {self.gpu_data['Temperature']}")
        else:
            lines.append(f"Temperature: {self.gpu_data.get('Temperature', 'N/A')}")
        
        # Memory usage with graphical representation  
        if "Memory Usage" in self.gpu_data and " / " in str(self.gpu_data["Memory Usage"]):
            memory_str = self.gpu_data["Memory Usage"]
            try:
                used_str, total_str = memory_str.split(" / ")
                used_val = float(used_str.replace(" MB", ""))
                total_val = float(total_str.replace(" MB", ""))
                memory_bar = self.create_progress_bar(used_val, total_val, bar_width, "Memory".ljust(11), "memory")
                lines.append(f"{memory_bar} ({used_val:.0f}/{total_val:.0f} MB)")
            except (ValueError, AttributeError):
                lines.append(f"Memory Usage: {self.gpu_data['Memory Usage']}")
        else:
            lines.append(f"Memory Usage: {self.gpu_data.get('Memory Usage', 'N/A')}")
        
        # Utilization with graphical representation
        if "Utilization" in self.gpu_data and self.gpu_data["Utilization"] != "N/A":
            util_str = self.gpu_data["Utilization"].replace(" %", "")
            try:
                util_val = float(util_str)
                util_bar = self.create_progress_bar(util_val, 100, bar_width, "Utilization".ljust(11), "generic")
                lines.append(f"{util_bar} ({util_val}%)")
            except ValueError:
                lines.append(f"Utilization: {self.gpu_data['Utilization']}")
        else:
            lines.append(f"Utilization: {self.gpu_data.get('Utilization', 'N/A')}")
        
        # Display any errors
        if "Error" in self.gpu_data:
            lines.append(f"Error: {self.gpu_data['Error']}")
        
        return "\n".join(lines)

    def get_gpu_count(self):
        try:
            cmd = ["nvidia-smi", "--query-gpu=count", "--format=csv,noheader,nounits"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                # nvidia-smi returns the count for each GPU, so count lines
                return len(result.stdout.strip().split('\n'))
        except:
            pass
        return 1  # Default to 1 GPU

    def next_gpu(self):
        gpu_count = self.get_gpu_count()
        self.gpu_id = (self.gpu_id + 1) % gpu_count
        self.update_gpu_data()

    def previous_gpu(self):
        gpu_count = self.get_gpu_count()
        self.gpu_id = (self.gpu_id - 1) % gpu_count
        self.update_gpu_data()

class NetworkStats(Static):
    interface = reactive("eth0")
    all_interfaces_data = reactive({})
    network_history = reactive([])  # Store historical data for graphing
    
    def on_mount(self):
        # Initialize network history for graphing (last 30 data points)
        self.network_history = []
        self.update_all_interfaces_data()
        self.set_interval(5, self.update_all_interfaces_data)

    def get_interface_info(self, interface_name):
        """Get detailed information for a specific interface"""
        try:
            # Get IP addresses
            ip_cmd = ["ip", "addr", "show", interface_name]
            ip_result = subprocess.run(ip_cmd, capture_output=True, text=True, timeout=3)
            
            # Get link status
            link_cmd = ["ip", "link", "show", interface_name]  
            link_result = subprocess.run(link_cmd, capture_output=True, text=True, timeout=3)
            
            interface_info = {
                "name": interface_name,
                "type": "Unknown",
                "status": "DOWN",
                "ip_addresses": [],
                "rx_bytes": 0,
                "tx_bytes": 0,
                "rx_errors": 0
            }
            
            # Determine interface type
            if "wl" in interface_name or "wifi" in interface_name.lower():
                interface_info["type"] = "WiFi"
            elif "eth" in interface_name or "en" in interface_name:
                interface_info["type"] = "Ethernet"
            elif "lo" in interface_name:
                interface_info["type"] = "Loopback"
            
            # Parse link status
            if link_result.returncode == 0:
                if "state UP" in link_result.stdout:
                    interface_info["status"] = "UP"
                    
            # Parse IP addresses
            if ip_result.returncode == 0:
                for line in ip_result.stdout.split('\n'):
                    if 'inet ' in line and 'scope global' in line:
                        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/(\d+)', line)
                        if match:
                            interface_info["ip_addresses"].append({
                                "address": match.group(1),
                                "cidr": match.group(2)
                            })
            
            return interface_info
            
        except Exception:
            return {
                "name": interface_name,
                "type": "Error",
                "status": "Error", 
                "ip_addresses": [],
                "rx_bytes": 0,
                "tx_bytes": 0,
                "rx_errors": 0
            }

    def update_all_interfaces_data(self):
        """Update data for all network interfaces and collect stats for graphing"""
        try:
            # Get all network interfaces
            available_interfaces = self.get_available_interfaces()
            
            # Get network statistics for all interfaces
            stats_cmd = ["cat", "/proc/net/dev"]
            stats_result = subprocess.run(stats_cmd, capture_output=True, text=True, timeout=5)
            
            interfaces_data = {}
            total_rx = 0
            total_tx = 0
            
            # Parse network statistics
            stats_by_interface = {}
            if stats_result.returncode == 0:
                for line in stats_result.stdout.split('\n'):
                    for iface in available_interfaces:
                        if iface + ':' in line:
                            parts = line.split()
                            if len(parts) >= 17:
                                rx_bytes = int(parts[1])
                                tx_bytes = int(parts[9])
                                rx_errors = int(parts[3])
                                stats_by_interface[iface] = {
                                    "rx_bytes": rx_bytes,
                                    "tx_bytes": tx_bytes, 
                                    "rx_errors": rx_errors
                                }
                                total_rx += rx_bytes
                                total_tx += tx_bytes
            
            # Get detailed info for WiFi and Ethernet interfaces
            wifi_interfaces = []
            ethernet_interfaces = []
            
            for iface in available_interfaces:
                if iface == "lo":  # Skip loopback
                    continue
                    
                interface_info = self.get_interface_info(iface)
                
                # Add traffic stats
                if iface in stats_by_interface:
                    interface_info.update(stats_by_interface[iface])
                
                if interface_info["type"] == "WiFi":
                    wifi_interfaces.append(interface_info)
                elif interface_info["type"] == "Ethernet":
                    ethernet_interfaces.append(interface_info)
                    
            # Store historical data for graphing (keep last 30 points)
            current_time = time.time()
            self.network_history.append({
                "time": current_time,
                "total_rx": total_rx,
                "total_tx": total_tx
            })
            
            # Keep only last 30 data points for graph
            if len(self.network_history) > 30:
                self.network_history = self.network_history[-30:]
                
            self.all_interfaces_data = {
                "wifi_interfaces": wifi_interfaces,
                "ethernet_interfaces": ethernet_interfaces,
                "total_rx": total_rx,
                "total_tx": total_tx,
                "history": self.network_history
            }
            
        except Exception as e:
            self.all_interfaces_data = {
                "wifi_interfaces": [],
                "ethernet_interfaces": [],
                "total_rx": 0,
                "total_tx": 0,
                "history": [],
                "error": str(e)
            }
            
        self.refresh()

    def create_network_graph(self, width=60, height=8):
        """Create an enhanced ASCII graph of network activity"""
        history = self.all_interfaces_data.get("history", [])
        if len(history) < 2:
            graph_lines = [""]  # Add empty line to match interface panel height
            graph_lines.append(Symbols.BOX_TOP_LEFT + Symbols.BOX_HORIZONTAL * width + Symbols.BOX_TOP_RIGHT)
            for _ in range(height):
                content = Symbols.PROGRESS_EMPTY * width
                graph_lines.append(Symbols.BOX_VERTICAL + content.ljust(width)[:width] + Symbols.BOX_VERTICAL)
            graph_lines.append(Symbols.BOX_BOTTOM_LEFT + Symbols.BOX_HORIZONTAL * width + Symbols.BOX_BOTTOM_RIGHT)
            graph_lines.append("[Collecting data...]")
            return graph_lines
            
        # Calculate throughput deltas (bytes per second)
        throughputs = []
        rx_rates = []
        tx_rates = []
        
        for i in range(1, len(history)):
            prev = history[i-1]
            curr = history[i]
            time_delta = curr["time"] - prev["time"]
            if time_delta > 0:
                rx_rate = (curr["total_rx"] - prev["total_rx"]) / time_delta
                tx_rate = (curr["total_tx"] - prev["total_tx"]) / time_delta
                total_rate = rx_rate + tx_rate
                throughputs.append(total_rate)
                rx_rates.append(rx_rate)
                tx_rates.append(tx_rate)
        
        if not throughputs:
            graph_lines = [""]  # Add empty line to match interface panel height
            graph_lines.append(Symbols.BOX_TOP_LEFT + Symbols.BOX_HORIZONTAL * width + Symbols.BOX_TOP_RIGHT)
            for _ in range(height):
                content = Symbols.PROGRESS_EMPTY * width
                graph_lines.append(Symbols.BOX_VERTICAL + content.ljust(width)[:width] + Symbols.BOX_VERTICAL)
            graph_lines.append(Symbols.BOX_BOTTOM_LEFT + Symbols.BOX_HORIZONTAL * width + Symbols.BOX_BOTTOM_RIGHT) 
            graph_lines.append("[No data available]")
            return graph_lines
            
        # Normalize values for graph
        max_throughput = max(throughputs) if throughputs else 1
        if max_throughput == 0:
            max_throughput = 1
            
        # Create multi-line graph  
        graph_lines = [""]  # Add empty line to match interface panel height
        
        # Take last 'width' values
        recent_throughputs = throughputs[-width:] if len(throughputs) >= width else throughputs
        recent_rx = rx_rates[-width:] if len(rx_rates) >= width else rx_rates
        recent_tx = tx_rates[-width:] if len(tx_rates) >= width else tx_rates
        
        # Add top border
        graph_lines.append(Symbols.BOX_TOP_LEFT + Symbols.BOX_HORIZONTAL * width + Symbols.BOX_TOP_RIGHT)
        
        # Create the graph from top to bottom
        for row in range(height):
            line = Symbols.BOX_VERTICAL  # Start with left border
            threshold = (height - row) / height
            
            # Build the graph content
            graph_content = ""
            for i, (total_rate, rx_rate, tx_rate) in enumerate(zip(recent_throughputs, recent_rx, recent_tx)):
                normalized_total = min(total_rate / max_throughput, 1.0)
                normalized_rx = min(rx_rate / max_throughput, 1.0) if max_throughput > 0 else 0
                normalized_tx = min(tx_rate / max_throughput, 1.0) if max_throughput > 0 else 0
                
                if normalized_total >= threshold:
                    if normalized_rx > normalized_tx:
                        graph_content += Symbols.PROGRESS_FILLED  # RX dominant - solid block
                    elif normalized_tx > normalized_rx:
                        graph_content += Symbols.PROGRESS_MEDIUM  # TX dominant - medium shade
                    else:
                        graph_content += Symbols.PROGRESS_EMPTY  # Equal - light shade
                else:
                    graph_content += " "
            
            # Ensure exact width and add right border
            graph_content = graph_content.ljust(width)[:width]  # Pad or truncate to exact width
            line = line + graph_content + Symbols.BOX_VERTICAL
                
            graph_lines.append(line)
        
        # Add bottom border
        graph_lines.append(Symbols.BOX_BOTTOM_LEFT + Symbols.BOX_HORIZONTAL * width + Symbols.BOX_BOTTOM_RIGHT)
        
        # Format max throughput for display
        if max_throughput > 1024*1024:
            max_str = f"{max_throughput/(1024*1024):.1f} MB/s"
        elif max_throughput > 1024:
            max_str = f"{max_throughput/1024:.1f} KB/s"
        else:
            max_str = f"{max_throughput:.0f} B/s"
            
        graph_lines.append(f"Max: {max_str}")
        graph_lines.append(f"{Symbols.PROGRESS_FILLED} RX  {Symbols.PROGRESS_MEDIUM} TX  {Symbols.PROGRESS_EMPTY} Both")
        
        return graph_lines

    def render(self):
        data = self.all_interfaces_data
        
        # Prepare interface information (left column)
        interface_lines = ["Network Interfaces:"]
        
        # Display Ethernet interfaces
        ethernet_interfaces = data.get("ethernet_interfaces", [])
        if ethernet_interfaces:
            interface_lines.append(f"{Symbols.ETHERNET_ICON} Ethernet:")
            for iface in ethernet_interfaces:
                status_icon = Symbols.STATUS_LOW if iface["status"] == "UP" else Symbols.STATUS_HIGH
                interface_lines.append(f"  {status_icon} {iface['name']}")
                
                if iface["ip_addresses"]:
                    for ip_info in iface["ip_addresses"]:
                        interface_lines.append(f"   {Symbols.IP_ICON} {ip_info['address']}/{ip_info['cidr']}")
                else:
                    interface_lines.append(f"   {Symbols.IP_ICON} No IP")
                    
                # Traffic stats (compact format)
                rx_mb = iface.get("rx_bytes", 0) / (1024*1024)
                tx_mb = iface.get("tx_bytes", 0) / (1024*1024)
                if rx_mb > 1024:
                    rx_str = f"{rx_mb/1024:.1f}GB"
                else:
                    rx_str = f"{rx_mb:.0f}MB"
                if tx_mb > 1024:
                    tx_str = f"{tx_mb/1024:.1f}GB"
                else:
                    tx_str = f"{tx_mb:.0f}MB"
                    
                interface_lines.append(f"   {Symbols.TRAFFIC_ICON} {Symbols.DOWNLOAD_ARROW}{rx_str} {Symbols.UPLOAD_ARROW}{tx_str}")
        
        # Display WiFi interfaces
        wifi_interfaces = data.get("wifi_interfaces", [])
        if wifi_interfaces:
            interface_lines.append(f"{Symbols.WIFI_ICON} WiFi:")
            for iface in wifi_interfaces:
                status_icon = Symbols.STATUS_LOW if iface["status"] == "UP" else Symbols.STATUS_HIGH
                interface_lines.append(f"  {status_icon} {iface['name']}")
                
                if iface["ip_addresses"]:
                    for ip_info in iface["ip_addresses"]:
                        interface_lines.append(f"   {Symbols.IP_ICON} {ip_info['address']}/{ip_info['cidr']}")
                else:
                    interface_lines.append(f"   {Symbols.IP_ICON} No IP")
                    
                # Traffic stats (compact format)
                rx_mb = iface.get("rx_bytes", 0) / (1024*1024)
                tx_mb = iface.get("tx_bytes", 0) / (1024*1024)
                if rx_mb > 1024:
                    rx_str = f"{rx_mb/1024:.1f}GB"
                else:
                    rx_str = f"{rx_mb:.0f}MB"
                if tx_mb > 1024:
                    tx_str = f"{tx_mb/1024:.1f}GB"
                else:
                    tx_str = f"{tx_mb:.0f}MB"
                    
                interface_lines.append(f"   {Symbols.TRAFFIC_ICON} {Symbols.DOWNLOAD_ARROW}{rx_str} {Symbols.UPLOAD_ARROW}{tx_str}")
        
        if not ethernet_interfaces and not wifi_interfaces:
            interface_lines.append(f"{Symbols.NO_DATA_ICON} No network interfaces")
        
        # Add total traffic at bottom of left column
        total_rx = data.get("total_rx", 0)
        total_tx = data.get("total_tx", 0)
        
        if total_rx > 1024*1024*1024:
            total_rx_str = f"{total_rx/(1024*1024*1024):.1f}GB"
        else:
            total_rx_str = f"{total_rx/(1024*1024):.0f}MB"
            
        if total_tx > 1024*1024*1024:
            total_tx_str = f"{total_tx/(1024*1024*1024):.1f}GB"  
        else:
            total_tx_str = f"{total_tx/(1024*1024):.0f}MB"
        
        interface_lines.append(f"{Symbols.TOTAL_ICON} Total: {Symbols.DOWNLOAD_ARROW}{total_rx_str} {Symbols.UPLOAD_ARROW}{total_tx_str}")
        
        # Display errors if any
        if "error" in data:
            interface_lines.append("")
            interface_lines.append(f"{Symbols.ERROR_ICON} Error: {data['error']}")
        
        return "\n".join(interface_lines)

    def get_available_interfaces(self):
        try:
            # Get real network interfaces and their status
            cmd = ["ip", "link", "show"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            interfaces = []
            active_interfaces = []
            
            if result.returncode == 0:
                current_interface = None
                for line in result.stdout.split('\n'):
                    # Look for interface names (format: "2: eth0: <BROADCAST...")
                    match = re.search(r'^\d+: ([^:@]+)', line)
                    if match:
                        interface_name = match.group(1)
                        # Skip virtual interfaces like veth, docker, etc.
                        if not any(skip in interface_name for skip in ['veth', 'docker', 'br-', 'virbr']):
                            current_interface = interface_name
                            interfaces.append(interface_name)
                            
                            # Check if interface is UP
                            if "state UP" in line:
                                active_interfaces.append(interface_name)
            
            # Prioritize active interfaces, then all interfaces
            if active_interfaces:
                # Put active interfaces first, then inactive ones
                inactive_interfaces = [iface for iface in interfaces if iface not in active_interfaces]
                interfaces = active_interfaces + inactive_interfaces
            
            return interfaces if interfaces else ["lo", "eth0", "wlan0"]  # Fallback
        except:
            return ["lo", "eth0", "wlan0"]  # Fallback

    def next_interface(self):
        interfaces = self.get_available_interfaces()
        if self.interface in interfaces:
            current_index = interfaces.index(self.interface)
            self.interface = interfaces[(current_index + 1) % len(interfaces)]
        else:
            self.interface = interfaces[0] if interfaces else "lo"
        self.update_net_data()

    def previous_interface(self):
        interfaces = self.get_available_interfaces()
        if self.interface in interfaces:
            current_index = interfaces.index(self.interface)
            self.interface = interfaces[(current_index - 1) % len(interfaces)]
        else:
            self.interface = interfaces[0] if interfaces else "lo"
        self.update_net_data()

class NetworkGraph(Static):
    """Separate widget for displaying network activity graph"""
    
    def __init__(self, network_stats_widget, **kwargs):
        super().__init__(**kwargs)
        self.network_stats = network_stats_widget
        self.set_interval(2.0, self.update_graph)
    
    def update_graph(self):
        """Update the graph display"""
        self.refresh()
    
    def render(self):
        """Render the network activity graph"""
        # Calculate available width and height based on widget size
        # Get widget dimensions, with fallbacks for minimum sizes
        available_width = max(self.size.width - 4, 20)  # Account for borders and minimum
        available_height = max(6, min(self.size.height - 4, 12))  # Reasonable height range
        
        # Use dynamic sizing based on available space
        graph_lines = self.network_stats.create_network_graph(width=available_width, height=available_height)
        return "\n".join(graph_lines)

class DockerStats(Static):
    docker_data = reactive([])

    def on_mount(self):
        self.update_docker_data()
        self.set_interval(10, self.update_docker_data)

    def update_docker_data(self):
        try:
            # Get Docker container information using docker ps -a
            cmd = ["docker", "ps", "-a", "--format", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            self.docker_data = []
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    try:
                        container_info = json.loads(line)
                        
                        # Get additional stats for running containers
                        cpu_usage = "0%"
                        memory_usage = "0 MB"
                        
                        if container_info.get("State") == "running":
                            try:
                                stats_cmd = ["docker", "stats", "--no-stream", "--format", "json", container_info["ID"]]
                                stats_result = subprocess.run(stats_cmd, capture_output=True, text=True, timeout=5)
                                if stats_result.returncode == 0 and stats_result.stdout.strip():
                                    stats_info = json.loads(stats_result.stdout.strip())
                                    cpu_usage = stats_info.get("CPUPerc", "0%")
                                    memory_usage = stats_info.get("MemUsage", "0 MB").split(' / ')[0]
                            except (json.JSONDecodeError, subprocess.TimeoutExpired):
                                pass  # Use default values
                        
                        container = {
                            "Container ID": container_info["ID"][:12],
                            "Name": container_info["Names"],
                            "Image": container_info["Image"],
                            "Status": container_info["State"],
                            "CPU": cpu_usage,
                            "Memory": memory_usage,
                            "Ports": container_info.get("Ports", "-")
                        }
                        self.docker_data.append(container)
                        
                    except json.JSONDecodeError:
                        continue  # Skip invalid JSON lines
                        
            if not self.docker_data:
                # No containers found
                self.docker_data = [{
                    "Container ID": "N/A",
                    "Name": "No containers found",
                    "Image": "N/A",
                    "Status": "N/A",
                    "CPU": "N/A",
                    "Memory": "N/A",
                    "Ports": "N/A"
                }]
                
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            # Docker not available or other error
            self.docker_data = [{
                "Container ID": "Error",
                "Name": f"Docker error: {str(e)}",
                "Image": "N/A",
                "Status": "N/A", 
                "CPU": "N/A",
                "Memory": "N/A",
                "Ports": "N/A"
            }]
            
        self.refresh()

    def _format_clickable_ports(self, ports_str):
        """Convert Docker port mappings to clickable links"""
        if not ports_str or ports_str in ["-", "N/A"]:
            return ports_str
            
        # For now, let's test with a simple approach to avoid markup errors
        # Parse different port formats:
        # "8080/tcp" -> "http://localhost:8080"
        # "0.0.0.0:5678->5678/tcp" -> "http://localhost:5678"
        
        try:
            clickable_ports = []
            port_mappings = [p.strip() for p in ports_str.split(',')]
            
            for port_mapping in port_mappings:
                port_match = None
                
                # Pattern 1: "0.0.0.0:5678->5678/tcp" or "[::]:5678->5678/tcp"
                external_port_match = re.search(r'(?:0\.0\.0\.0|\[::\]):(\d+)->', port_mapping)
                if external_port_match:
                    port_match = external_port_match.group(1)
                
                # Pattern 2: Simple port "8080/tcp"
                if not port_match:
                    simple_port_match = re.search(r'^(\d+)/(tcp|udp)$', port_mapping.strip())
                    if simple_port_match:
                        port_match = simple_port_match.group(1)
                
                if port_match:
                    # Create a simple clickable link
                    url = f"http://localhost:{port_match}"
                    # Use a safer link format
                    clickable_link = f"[link={url}]{port_mapping}[/link]"
                    clickable_ports.append(clickable_link)
                else:
                    # If no port found, keep original text
                    clickable_ports.append(port_mapping)
            
            return ", ".join(clickable_ports)
        except Exception:
            # If any error occurs, return the original string
            return ports_str

    def render(self):
        lines = ["Docker Containers:"]
        
        running_containers = [c for c in self.docker_data if c["Status"] == "running"]
        stopped_containers = [c for c in self.docker_data if c["Status"] != "running"]
        
        if running_containers:
            lines.append("Running Containers:")
            for container in running_containers:
                lines.append(f"  {Symbols.CONTAINER_RUNNING} {container['Name']}")
                lines.append(f"     Image: {container['Image']}")
                lines.append(f"     CPU: {container['CPU']} | Mem: {container['Memory']}")
                
                # Make ports clickable (temporarily disabled due to markup issue)
                # clickable_ports = self._format_clickable_ports(container['Ports'])
                # For now, show ports with simple formatting and add instruction
                ports_display = container['Ports']
                if ports_display and ports_display not in ["-", "N/A"]:
                    # Extract port numbers for user reference
                    port_matches = re.findall(r'(\d+)', ports_display)
                    if port_matches:
                        unique_ports = list(set(port_matches))
                        port_hint = f" (try: http://localhost:{unique_ports[0]})" if len(unique_ports) == 1 else f" (try ports: {', '.join(unique_ports)})"
                        lines.append(f"     Ports: {ports_display}{port_hint}")
                    else:
                        lines.append(f"     Ports: {ports_display}")
                else:
                    lines.append(f"     Ports: {ports_display}")
        
        if stopped_containers:
            lines.append("Stopped/Exited Containers:")
            for container in stopped_containers:
                status_icon = Symbols.CONTAINER_STOPPED if container['Status'] == "stopped" else Symbols.CONTAINER_ERROR
                lines.append(f"  {status_icon} {container['Name']} ({container['Status']})")
        
        return "\n".join(lines)
    
    def toggle_container(self, container_id):
        for container in self.docker_data:
            if container["Container ID"] == container_id:
                container["Status"] = "running" if container["Status"] == "stopped" else "stopped"
        self.refresh()
        self.update_docker_data()

class CustomHeader(Static):
    """Custom header showing system monitor title and current date/time"""
    
    def on_mount(self):
        self.set_interval(1, self.update_time)  # Update every second
        self.update_time()
    
    def update_time(self):
        current_time = datetime.now()
        date_str = current_time.strftime("%A, %B %d, %Y")
        time_str = current_time.strftime("%H:%M:%S")
        self.update(f"{Symbols.GPU_ICON} System Monitor    {Symbols.CALENDAR_ICON} {date_str}    {Symbols.CLOCK_ICON} {time_str}")

class LogPanel(Log):
    def on_mount(self):
        self.set_interval(2, self.add_log_entry)

    def add_log_entry(self):
        self.write(f"Log entry at {time.strftime('%X')}")
        self.scroll_end(animate=False)

class SystemMonitorApp(App):
    CSS_PATH = "styles.css"
    
    # Reactive variable to control log panel visibility
    show_log_panel = reactive(False)  # Default to hidden
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("g", "next_gpu", "Next GPU"),
        ("G", "previous_gpu", "Previous GPU"),
        ("n", "next_interface", "Next Interface"),
        ("N", "previous_interface", "Previous Interface"),
        ("d", "toggle_docker_1", "Toggle Docker 1"),
        ("D", "toggle_docker_2", "Toggle Docker 2"),
        ("l", "toggle_log_panel", "Toggle Log Panel"),
    ]

    def compose(self) -> ComposeResult:
        yield CustomHeader(id="header")
        with Container():
            # GPU Stats and Processes side by side at the top
            with Horizontal():
                self.gpu_stats = GPUStats(id="gpu-panel")
                self.gpu_stats.border_title = f"{Symbols.GPU_ICON}  GPU Statistics"
                yield self.gpu_stats
                
                self.gpu_process_table = GPUProcessTable(id="gpu-process-table")
                yield self.gpu_process_table
            
            # Create network panels side by side below GPU stats
            with Horizontal():
                self.net_stats = NetworkStats(id="network-panel")
                self.net_stats.border_title = f"{Symbols.NETWORK_ICON} Network Interfaces"
                self.net_graph = NetworkGraph(self.net_stats, id="network-graph-panel")
                self.net_graph.border_title = f"{Symbols.GRAPH_ICON} Network Activity"
                yield self.net_stats
                yield self.net_graph
            
            # Docker stats below network panels
            self.docker_stats = DockerStats(id="docker-panel")
            self.docker_stats.border_title = f"{Symbols.DOCKER_ICON} Docker Containers"
            yield self.docker_stats
            
            # Create log panel but don't yield it yet (it starts hidden)
            self.log_panel = LogPanel(id="log-panel")
            self.log_panel.border_title = f"{Symbols.LOG_ICON} System Log"
            self.log_panel.display = False  # Start hidden
            yield self.log_panel  # Always yield it, but control visibility via display property
        yield Footer()

    def action_next_gpu(self):
        self.gpu_stats.next_gpu()
        # Update the process table with the new GPU's processes
        if hasattr(self, 'gpu_process_table'):
            self.gpu_process_table.update_processes(self.gpu_stats.running_processes)

    def action_previous_gpu(self):
        self.gpu_stats.previous_gpu()
        # Update the process table with the new GPU's processes
        if hasattr(self, 'gpu_process_table'):
            self.gpu_process_table.update_processes(self.gpu_stats.running_processes)

    def action_next_interface(self):
        self.net_stats.next_interface()

    def action_previous_interface(self):
        self.net_stats.previous_interface()

    def action_toggle_docker_1(self):
        self.docker_stats.toggle_container("1")

    def action_toggle_docker_2(self):
        self.docker_stats.toggle_container("2")

    def action_toggle_log_panel(self):
        """Toggle the visibility of the log panel"""
        self.show_log_panel = not self.show_log_panel

    def watch_show_log_panel(self, show_log: bool) -> None:
        """Watch for changes to show_log_panel and update panel visibility"""
        if hasattr(self, 'log_panel'):
            self.log_panel.display = show_log
            if show_log:
                # Scroll to the log panel when showing it
                self.call_after_refresh(self.log_panel.scroll_visible)

if __name__ == "__main__":
    app = SystemMonitorApp()
    app.run()

   
