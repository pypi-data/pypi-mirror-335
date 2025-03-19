import asyncio
import threading
import time
from textual.containers import HorizontalGroup
from textual.widgets import Button, Input, DataTable, Sparkline
from scapy.all import IP, TCP, UDP, sniff
from terminet.network_table import NetworkTable
from textual.app import ComposeResult


class Monitor(HorizontalGroup):
    """Class for maintaining textual buttons and handling the necessities
       for reading network data."""

    def __init__(self, network_table: NetworkTable):
        super().__init__()
        self.__network_table = network_table
        self.__start_time = time.time()
        self.__sniffing_thread = None
        self.__running = False
        self.__iface = Input(
            placeholder="Enter your internet interface (e.g., eth0, wlan0)"
        )
        self.__protocol_map = {
            1: "ICMP", 6: "TCP", 17: "UDP", 58: "ICMPv6", 132: "SCTP"
        }

    def compose(self) -> ComposeResult:
        """Create buttons for app."""
        yield self.__iface
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Clear", id="clear", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events for starting and stopping app."""
        btn_event = event.button.id
        if btn_event == "start":
            if not self.__running:
                asyncio.create_task(self.start_sniffing())
                self.app.notify("Starting packet capture")
                self.add_class("started")
        elif btn_event == "stop":
            self.__running = False
            self.app.notify("Stopping packet capture")
            self.remove_class("started")
        elif btn_event == "clear":
            if self.__running:
                self.app.notify("Stop app to clear data")
            else:
                table = self.__network_table.query_one(DataTable)
                table.clear()
                graph = self.__network_table.query_one(Sparkline)
                graph.data.clear()
                graph.refresh()

    async def start_sniffing(self) -> None:
        """Start sniffing network packets in seperate thread."""
        self.__running = True
        self.__sniffing_thread = threading.Thread(
            target=self.sniff_packets,
            daemon=True
        )
        self.__sniffing_thread.start()

    def sniff_packets(self) -> None:
        """Sniff packets using Scapy sniff on the interface provided by the user."""
        interface = self.__iface.value.strip()
        try:
            # Use specified interface if provided.
            if interface:
                self.app.notify(f"Sniffing on interface: {interface}")
            else:
                interface = "eth0"
                self.app.notify(
                    f"No interface specified, using default {interface}")
            sniff(
                iface=interface,
                prn=self.packet_handler,
                store=False,
                stop_filter=lambda _: not self.__running
            )
        except Exception as e:
            self.app.notify(f"Error: ", e)
            self.__running = False

    def packet_handler(self, packet) -> None:
        """Filter network packets that contain an IP. Call helper methods
           to extract packet information and update app widgets (network table, sparkline)."""
        if IP in packet:
            packet_info = self.get_packet_info(packet)
            self.app.call_from_thread(self.add_packet_to_table, packet_info)
            self.app.call_from_thread(
                self.add_bandwidth_to_sparkline, packet_info["size"])

    def get_packet_info(self, packet) -> dict:
        """Extract network packet information and store it in a hash table."""
        packet_info = {
            "source": packet[IP].src,
            "destination": packet[IP].dst,
            "protocol": self.get_protocol_name(packet[IP].proto),
            "size": len(packet),
            "sport": None,
            "dport": None
        }
        if TCP in packet:
            packet_info.update(
                {"sport": packet[TCP].sport, "dport": packet[TCP].dport}
            )
        elif UDP in packet:
            packet_info.update(
                {"sport": packet[UDP].sport, "dport": packet[UDP].dport}
            )
        return packet_info

    def get_protocol_name(self, proto_num: int) -> str:
        """Return the associated protocol mapped to protocol number parameter."""
        return self.__protocol_map.get(proto_num, f"OTHER {proto_num}")

    def add_packet_to_table(self, packet_info) -> None:
        """Update the network table with the network packet information stored
           in a tuple."""
        tup = (
            packet_info["source"], packet_info["destination"], packet_info["protocol"],
            packet_info["sport"], packet_info["dport"], packet_info["size"]
        )
        self.__network_table.update_table(tup)

    def add_bandwidth_to_sparkline(self, packet_size) -> None:
        """Calculate bandwidth usage based on the size of the packet divided by 1024 to get KB/s."""
        elapsed_time = time.time() - self.__start_time
        if elapsed_time > 0:
            bandwidth_kbps = packet_size / (elapsed_time * (1000*1024*8))
            self.__network_table.update_graph(bandwidth_kbps)
