import asyncio
from textual.widget import Widget
from textual.widgets import DataTable, Sparkline, Label
from textual.app import ComposeResult


class NetworkTable(Widget):
    """Class for creating widgtes to display network data in tabular format and 
       bandwidth usage sparkline graph."""

    def compose(self) -> ComposeResult:
        """Created DataTable and Sparkline widgets."""
        yield Label("Bandwidth usage (KB/s)")
        self.graph = Sparkline()
        yield self.graph

        self.table = DataTable()
        self.table.add_columns(
            "Source", "Destination", "Protocol", "Source Port", "Destination Port", "Size"
        )
        yield self.table

    def update_table(self, tup: tuple) -> None:
        """Add a new row to the data table."""
        src, dst, proto, sport, dport, size = tup
        self.table.add_row(src, dst, proto, sport, dport, size)
        asyncio.sleep(0.5)

    def update_graph(self, bandwidth) -> None:
        """Handle updating the sparkline graph by appending bandwidth usage which will
           be calculated by the size of the packet / 1024."""
        if not hasattr(self.graph, 'data') or self.graph.data is None:
            self.graph.data = [0]
        self.graph.data.append(bandwidth)
        if len(self.graph.data) > 100:
            self.graph.data = self.graph.data[-100:]
        asyncio.sleep(0.5)
