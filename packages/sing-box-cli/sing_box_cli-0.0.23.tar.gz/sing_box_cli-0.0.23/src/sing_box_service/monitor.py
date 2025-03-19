import asyncio
import math
import statistics
from collections import deque
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np
import plotext as plt  # type: ignore
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from scipy.interpolate import PchipInterpolator, make_interp_spline

from .client import SingBoxAPIClient
from .widget import RichPlotMixin, create_header_panel


class RefreshRate(Enum):
    """Refresh rate options for stats display."""

    SLOW = 1.0
    NORMAL = 0.5
    FAST = 0.25


def format_bytes(num_bytes_i: int | float) -> str:
    """
    Format bytes to human-readable format.

    Args:
        num_bytes: Number of bytes

    Returns:
        Formatted string representation in bytes
    """
    num_bytes = float(num_bytes_i)
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024.0 or unit == "GB":
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0

    # This line should never be reached due to the "GB" condition above,
    # but is needed to satisfy the type checker
    return f"{num_bytes:.2f} GB"


def format_speed(bytes_per_sec_i: int | float) -> str:
    """
    Format network speed to human-readable format.

    Args:
        bytes_per_sec: Speed in kilobits per second (B/s)

    Returns:
        Formatted string representation in bytes per second
    """
    bytes_per_sec = float(bytes_per_sec_i)
    for unit in ["B/s", "KB/s", "MB/s", "GB/s"]:
        if bytes_per_sec < 1024.0 or unit == "GB/s":
            return f"{bytes_per_sec:.2f} {unit}"
        bytes_per_sec /= 1024.0

    # This line should never be reached due to the "GB/s" condition above,
    # but is needed to satisfy the type checker
    return f"{bytes_per_sec:.2f} GB/s"


def calculate_averages(
    data_history: deque[dict[str, int]], key: str
) -> tuple[float, float]:
    """
    Calculate 5s and 10s averages for a specific metric.

    Args:
        data_history: Deque containing historical data
        key: The key to extract from each data point

    Returns:
        Tuple of (5s_avg, 10s_avg)
    """
    history_len = len(data_history)

    # Calculate 5s average (or less if not enough history)
    five_sec_samples = (
        list(data_history)[-5:] if history_len >= 5 else list(data_history)
    )
    five_sec_avg = (
        statistics.mean(item.get(key, 0) for item in five_sec_samples)
        if five_sec_samples
        else 0
    )

    # Calculate 10s average (or less if not enough history)
    ten_sec_samples = (
        list(data_history)[-10:] if history_len >= 10 else list(data_history)
    )
    ten_sec_avg = (
        statistics.mean(item.get(key, 0) for item in ten_sec_samples)
        if ten_sec_samples
        else 0
    )

    return five_sec_avg, ten_sec_avg


def sort_connections(connections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Sort connections by time in descending order.

    This function takes a list of connection dictionaries and sorts them primarily by the 'start' time
    and secondarily by the 'host' field, both in descending order.

    Args:
        connections (list[dict[str, Any]]): A list of dictionaries representing connections.
            Each dictionary should contain 'start' and 'host' keys.

    Returns:
        list[dict[str, Any]]: The sorted list of connection dictionaries.
    """
    return sorted(
        connections, key=lambda x: (x.get("start", ""), x.get("host", "")), reverse=True
    )


def format_rule(rule: str) -> str:
    """
    Format a rule string for display.

    This function takes a rule string and extracts the relevant parts for display.
    It tries to extract the rule pattern, e.g., from "rule_set=proxy-rule => route(proxy)".

    Args:
        rule (str): The rule string to format.

    Returns:
        str: The formatted rule string.
    """
    if rule:
        if "=>" in rule:
            rule_parts = rule.split("=>")
            return rule_parts[0].strip()
        return rule
    else:
        raise ValueError(f"Invalid rule data: {rule}")


def format_duration(start_str: str) -> str:
    """
    Calculate the duration of a connection.

    This function takes a start time string and calculates the duration from the start time to the current time.

    Args:
        start_str (str): The start time string in ISO format.

    Returns:
        str: The duration string in seconds.
    """
    try:
        # Parse ISO format time and calculate duration
        start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        now = datetime.now(tz=start_time.tzinfo)
        duration = now - start_time
        seconds = int(duration.total_seconds())
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        elif seconds < 86400:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
        else:
            return f"{seconds // 86400}d {(seconds % 86400) // 3600}h"
    except (ValueError, TypeError):
        raise ValueError(f"Invalid start time: {start_str}")


def format_chain(chains: list[str]) -> str:
    """
    Format a chain list for display.

    This function takes a list of chain names and formats them for display.

    Args:
        chains (list[str]): A list of chain names.

    Returns:
        str: The formatted chain string.
    """
    if chains:
        return " → ".join(reversed(chains))
    else:
        raise ValueError(f"Invalid chains data: {chains}")


def interpolate_data(
    data: list[float], method: str = "linear", factor: int = 5
) -> tuple[list[float], list[float]]:
    """
    Interpolate data points to create a smoother curve.

    Args:
        data: List of data points to interpolate
        method: Interpolation method ('spline', 'pchip', or 'linear')

    Returns:
        Tuple of (x_new, y_new) containing interpolated data points
    """
    if len(data) < 3:
        # Not enough points for interpolation, return original data
        return list(range(len(data))), data

    x = np.array(range(len(data)))
    y = np.array(data)

    # Create new x values for interpolated points
    points = len(data) * factor
    x_new = np.linspace(x.min(), x.max(), points)

    if method == "spline":
        # Cubic spline interpolation
        spl = make_interp_spline(x, y, k=3)  # k=3 for cubic spline
        y_new = spl(x_new)
    elif method == "pchip":
        # PCHIP interpolation (Piecewise Cubic Hermite Interpolating Polynomial)
        # This preserves monotonicity and doesn't overshoot
        pchip = PchipInterpolator(x, y)
        y_new = pchip(x_new)
    else:  # 'linear' or any other value
        # Simple linear interpolation
        y_new = np.interp(x_new, x, y)

    return list(x_new), list(y_new)


class TrafficGraph(RichPlotMixin):
    """A Rich-compatible network traffic graph using plotext."""

    def __init__(self, max_points: int = 60) -> None:
        """
        Initialize the traffic graph.

        Args:
            max_points: Maximum number of data points to keep
        """
        super().__init__()

        self.max_points = max_points
        # Initialize data structures for storing history
        # At least 2 points needed for a line o avoid rendering issues
        self.upload_speeds: deque[float] = deque([0.0, 0.0], maxlen=max_points)
        self.download_speeds: deque[float] = deque([0.0, 0.0], maxlen=max_points)

        # Number of points to generate during inte= 5
        self.interp_factor = 5

    def update_from_traffic_data(self, traffic_data: dict[str, Any]) -> None:
        """
        Update the graph with new traffic data.

        Args:
            traffic_data: Dictionary with 'up' and 'down' traffic totals
        """

        # Update the graph with new data
        self.upload_speeds.append(traffic_data.get("up", 0))
        self.download_speeds.append(traffic_data.get("down", 0))

    def make_plot(self, width: int, height: int, interp_method: str = "pchip") -> str:
        """
        Create the plot with interpolated data.

        Args:
            width: Width of the plot
            height: Height of the plot
            interp_method: Interpolation method ('spline', 'pchip', or 'linear')

        Returns:
            String representation of the plot
        """
        # Clear the previous plot
        plt.clf()

        # Set up the plot styling
        plt.theme("dark")
        plt.axes_color((10, 14, 27))
        plt.ticks_color((133, 159, 213))
        plt.plotsize(width, height)

        # Set titles and legend
        plt.xlabel("Time")
        plt.ylabel("Speed")

        # Get the data for plotting
        y_upload = list(self.upload_speeds)
        y_download = list(self.download_speeds)

        if len(y_upload) >= 2 and len(y_download) >= 2:
            # Interpolate data
            x_upload, y_upload_smooth = interpolate_data(
                y_upload, interp_method, self.interp_factor
            )
            x_download, y_download_smooth = interpolate_data(
                y_download, interp_method, self.interp_factor
            )

            # Plot upload and download data with interpolated values
            plt.plot(
                x_upload,
                y_upload_smooth,
                marker=".",
                label="Upload",
                color=(255, 73, 112),  # Red
            )
            plt.plot(
                x_download,
                y_download_smooth,
                marker=".",
                label="Download",
                color=(68, 180, 255),  # Blue
            )

            # Calculate and set y-axis ticks with a better algorithm
            all_y_values = y_upload_smooth + y_download_smooth
            max_y_value = max(all_y_values) if all_y_values else 1.0

            # Ensure we have a reasonable minimum value
            max_y_value = max(max_y_value, 1.0)

            # Round up to a nice number for the maximum tick
            # Find the magnitude of the value (1, 10, 100, 1000, etc.)
            magnitude = 10 ** math.floor(math.log10(max_y_value))

            # Scale to a number between 1-10
            scaled = max_y_value / magnitude

            # Round up to a nice number (1, 2, 5, 10)
            if scaled <= 1:
                nice_max = 1
            elif scaled <= 2:
                nice_max = 2
            elif scaled <= 5:
                nice_max = 5
            else:
                nice_max = 10

            # Final nice maximum value
            nice_max_value = nice_max * magnitude

            # Create ticks with appropriate intervals
            num_ticks = 8  # Will give 7 intervals
            y_ticks = [i * (nice_max_value / (num_ticks - 1)) for i in range(num_ticks)]

            # Create labels
            y_labels = [format_speed(val) for val in y_ticks]

            # Apply ticks to the plot
            plt.yticks(y_ticks, y_labels)

            return str(plt.build())
        else:
            return "Collecting data..."


class ResourceVisualizer:
    """Class for visualizing Sing-Box resource statistics."""

    def __init__(self, refresh_rate: float = RefreshRate.FAST.value) -> None:
        """Initialize the visualizer with data history tracking."""
        self.refresh_rate = refresh_rate
        self.console = Console()

        # For averages calculation
        self.traffic_data_history: deque[dict[str, int]] = deque(maxlen=10)
        self.memory_data_history: deque[dict[str, int]] = deque(maxlen=10)

        # For traffic graph
        self.traffic_graph = TrafficGraph(
            max_points=120  # Store 2 minutes of data
        )

    def create_traffic_table(self, traffic_data: dict[str, Any]) -> Table:
        """Create a table displaying traffic statistics with averages."""
        # Add current data to history
        self.traffic_data_history.append(traffic_data.copy())

        # Get the raw values
        up_bytes = traffic_data.get("up", 0)
        down_bytes = traffic_data.get("down", 0)

        # Calculate averages
        up_5s_avg, up_10s_avg = calculate_averages(self.traffic_data_history, "up")
        down_5s_avg, down_10s_avg = calculate_averages(
            self.traffic_data_history, "down"
        )

        # Create table with expanded columns
        table = Table(title="Network Traffic", expand=True)
        table.add_column("Direction", style="cyan")
        table.add_column("Current", justify="right", style="green", width=10)
        table.add_column("5s Avg", justify="right", style="yellow", width=10)
        table.add_column("10s Avg", justify="right", style="bright_blue", width=10)

        # Add rows with current values and averages
        table.add_row(
            "Upload",
            format_speed(up_bytes),
            format_speed(up_5s_avg),
            format_speed(up_10s_avg),
        )
        table.add_row(
            "Download",
            format_speed(down_bytes),
            format_speed(down_5s_avg),
            format_speed(down_10s_avg),
        )
        return table

    def create_memory_table(self, memory_data: dict[str, Any]) -> Table:
        """Create a table displaying memory usage statistics with averages."""
        # Add current data to history
        self.memory_data_history.append(memory_data.copy())

        # Extract current memory values
        inuse = memory_data.get("inuse", 0)
        total = memory_data.get("total", 0)

        # Calculate averages
        inuse_5s_avg, inuse_10s_avg = calculate_averages(
            self.memory_data_history, "inuse"
        )
        total_5s_avg, total_10s_avg = calculate_averages(
            self.memory_data_history, "total"
        )

        # Create table with expanded columns
        table = Table(title="Memory Usage", expand=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Current", justify="right", style="green", width=10)
        table.add_column("5s Avg", justify="right", style="yellow", width=10)
        table.add_column("10s Avg", justify="right", style="bright_blue", width=10)

        # Add rows with current values and averages
        table.add_row(
            "In Use",
            format_bytes(inuse),
            format_bytes(inuse_5s_avg),
            format_bytes(inuse_10s_avg),
        )
        table.add_row(
            "Total Allocated",
            format_bytes(total),
            format_bytes(total_5s_avg),
            format_bytes(total_10s_avg),
        )

        # Add usage percentage if total is not zero
        if total > 0:
            current_percent = (inuse / total) * 100
            avg_5s_percent = (inuse_5s_avg / total) * 100 if total else 0
            avg_10s_percent = (inuse_10s_avg / total) * 100 if total else 0

            table.add_row(
                "Usage",
                f"{current_percent:.1f}%",
                f"{avg_5s_percent:.1f}%",
                f"{avg_10s_percent:.1f}%",
            )

        return table

    def create_resources_layout(
        self, traffic_data: dict[str, Any], memory_data: dict[str, Any]
    ) -> Layout:
        """Create the main layout with all resource components."""
        layout = Layout()

        # Create main sections
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=1),
        )

        # Split main section for tables and graph
        layout["main"].split(
            Layout(name="stats", ratio=1), Layout(name="graph", ratio=3)
        )

        # Split stats section into left and right
        layout["stats"].split_row(
            Layout(name="traffic_stats"), Layout(name="memory_stats")
        )

        # Add components
        layout["header"].update(create_header_panel("Sing-Box Resource Monitor"))

        # Add tables
        layout["stats"]["traffic_stats"].update(self.create_traffic_table(traffic_data))
        layout["stats"]["memory_stats"].update(self.create_memory_table(memory_data))

        # Update the traffic graph with new data
        self.traffic_graph.update_from_traffic_data(traffic_data)

        # Add the traffic graph to the layout
        layout["graph"].update(
            Panel(
                self.traffic_graph,
                title="Network Traffic Over Time",
                border_style="cyan",
            )
        )

        # Add footer
        layout["footer"].update(Text("Press Ctrl+C to exit", justify="center"))

        return layout


class ResourceMonitor:
    """Class that connects the API client with visualization for resource monitoring."""

    def __init__(
        self, api_client: SingBoxAPIClient, visualizer: ResourceVisualizer
    ) -> None:
        """
        Initialize the resource monitor.

        Args:
            api_client: SingBox API client
            visualizer: Resource visualizer
        """
        self.api_client = api_client
        self.visualizer = visualizer
        self.running = False
        self.current_traffic = {"up": 0, "down": 0}  # in bytes
        self.current_memory = {"inuse": 0, "total": 0}  # in bytes

    async def monitor_traffic(self) -> None:
        """Monitor traffic stream from the API."""
        try:
            async for traffic_data in self.api_client.traffic_stream():
                self.current_traffic = traffic_data
                if not self.running:
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.visualizer.console.print(f"[red]Error monitoring traffic: {str(e)}")

    async def monitor_memory(self) -> None:
        """Monitor memory stream from the API."""
        try:
            async for memory_data in self.api_client.memory_stream():
                self.current_memory = memory_data
                if not self.running:
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.visualizer.console.print(f"[red]Error monitoring memory: {str(e)}")

    async def refresh_display(self) -> None:
        """Main display refresh loop."""
        self.running = True
        # Start monitoring in separate tasks
        traffic_task = asyncio.create_task(self.monitor_traffic())
        memory_task = asyncio.create_task(self.monitor_memory())
        with Live(
            refresh_per_second=1 / self.visualizer.refresh_rate, screen=True
        ) as live:
            while self.running:
                try:
                    # Use the current data from the streams
                    traffic_data = self.current_traffic
                    memory_data = self.current_memory

                    # Update display
                    layout = self.visualizer.create_resources_layout(
                        traffic_data, memory_data
                    )
                    live.update(layout)

                    # Wait for next refresh
                    await asyncio.sleep(self.visualizer.refresh_rate - 0.1)
                except KeyboardInterrupt:
                    self.running = False
                    break
                except Exception as e:
                    live.update(
                        Panel(
                            f"Unexpected error: {str(e)}",
                            title="Error",
                            border_style="red",
                        )
                    )
                    await asyncio.sleep(2)

        # Clean up monitoring tasks
        self.running = False
        traffic_task.cancel()
        memory_task.cancel()
        try:
            await asyncio.gather(traffic_task, memory_task, return_exceptions=True)
        except asyncio.CancelledError:
            pass

    async def start(self) -> None:
        """Start the resource monitor."""
        try:
            await self.refresh_display()
        except KeyboardInterrupt:
            self.running = False
            self.visualizer.console.print("Exiting resource monitor...")
