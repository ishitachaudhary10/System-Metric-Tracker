import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from logger import LogManager

class Visualizer:
    def __init__(self):
        self.log_manager = LogManager()
        
    def plot_usage_trends(self, days=1):
        """
        Generate line charts for CPU and RAM usage over time
        Args: days - number of days to plot
        """
        try:
            # Read log data
            data = self.log_manager.read_log_data(days)
            
            if not data:
                print("No data available to plot")
                return
            
            # Extract data for plotting
            timestamps = [entry['timestamp'] for entry in data]
            cpu_usage = [entry['cpu_percent'] for entry in data]
            memory_usage = [entry['memory_percent'] for entry in data]
            disk_usage = [entry['disk_percent'] for entry in data]
            
            # Create figure with subplots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
            fig.suptitle(f'System Resource Usage - Last {days} Day(s)', fontsize=16)
            
            # Plot CPU usage
            ax1.plot(timestamps, cpu_usage, color='red', linewidth=2, label='CPU Usage')
            ax1.set_ylabel('CPU Usage (%)')
            ax1.set_title('CPU Usage Over Time')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            ax1.set_ylim(0, 100)
            
            # Add CPU threshold line
            ax1.axhline(y=80, color='red', linestyle='--', alpha=0.7, label='Alert Threshold')
            
            # Plot Memory usage
            ax2.plot(timestamps, memory_usage, color='blue', linewidth=2, label='RAM Usage')
            ax2.set_ylabel('RAM Usage (%)')
            ax2.set_title('RAM Usage Over Time')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            ax2.set_ylim(0, 100)
            
            # Plot Disk usage
            ax3.plot(timestamps, disk_usage, color='green', linewidth=2, label='Disk Usage')
            ax3.set_ylabel('Disk Usage (%)')
            ax3.set_xlabel('Time')
            ax3.set_title('Disk Usage Over Time')
            ax3.grid(True, alpha=0.3)
            ax3.legend()
            ax3.set_ylim(0, 100)
            
            # Format x-axis
            for ax in [ax1, ax2, ax3]:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            # Adjust layout and save
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"usage_plot_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            
            print(f"Usage plot saved as: {filename}")
            
            # Close plot to free memory
            plt.close()
            
        except Exception as e:
            print(f"Error generating usage plots: {e}")
    
    def plot_resource_comparison(self, days=1):
        """
        Generate a comparison chart of all resources
        Args: days - number of days to plot
        """
        try:
            # Read log data
            data = self.log_manager.read_log_data(days)
            
            if not data:
                print("No data available to plot")
                return
            
            # Extract data for plotting
            timestamps = [entry['timestamp'] for entry in data]
            cpu_usage = [entry['cpu_percent'] for entry in data]
            memory_usage = [entry['memory_percent'] for entry in data]
            disk_usage = [entry['disk_percent'] for entry in data]
            
            # Create figure
            plt.figure(figsize=(12, 8))
            
            # Plot all resources
            plt.plot(timestamps, cpu_usage, color='red', linewidth=2, label='CPU Usage', alpha=0.8)
            plt.plot(timestamps, memory_usage, color='blue', linewidth=2, label='RAM Usage', alpha=0.8)
            plt.plot(timestamps, disk_usage, color='green', linewidth=2, label='Disk Usage', alpha=0.8)
            
            # Add CPU threshold line
            plt.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='CPU Alert Threshold')
            
            plt.title(f'System Resource Usage Comparison - Last {days} Day(s)', fontsize=16)
            plt.xlabel('Time')
            plt.ylabel('Usage (%)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.ylim(0, 100)
            
            # Format x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))
            plt.setp(plt.gca().xaxis.get_majorticklabels(), rotation=45)
            
            # Adjust layout and save
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"resource_comparison_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            
            print(f"Resource comparison plot saved as: {filename}")
            
            # Close plot to free memory
            plt.close()
            
        except Exception as e:
            print(f"Error generating resource comparison plot: {e}")
    
    def generate_summary_stats(self, days=1):
        """
        Generate summary statistics for the specified period
        Args: days - number of days to analyze
        """
        try:
            # Read log data
            data = self.log_manager.read_log_data(days)
            
            if not data:
                print("No data available for analysis")
                return
            
            # Calculate statistics
            cpu_values = [entry['cpu_percent'] for entry in data]
            memory_values = [entry['memory_percent'] for entry in data]
            disk_values = [entry['disk_percent'] for entry in data]
            
            print(f"\n=== Summary Statistics - Last {days} Day(s) ===")
            print(f"Data Points: {len(data)}")
            print(f"Time Period: {data[0]['timestamp']} to {data[-1]['timestamp']}")
            print()
            
            # CPU statistics
            print("CPU Usage:")
            print(f"  Average: {sum(cpu_values)/len(cpu_values):.1f}%")
            print(f"  Maximum: {max(cpu_values):.1f}%")
            print(f"  Minimum: {min(cpu_values):.1f}%")
            print(f"  Above 80%: {sum(1 for x in cpu_values if x > 80)} times")
            print()
            
            # Memory statistics
            print("RAM Usage:")
            print(f"  Average: {sum(memory_values)/len(memory_values):.1f}%")
            print(f"  Maximum: {max(memory_values):.1f}%")
            print(f"  Minimum: {min(memory_values):.1f}%")
            print()
            
            # Disk statistics
            print("Disk Usage:")
            print(f"  Average: {sum(disk_values)/len(disk_values):.1f}%")
            print(f"  Maximum: {max(disk_values):.1f}%")
            print(f"  Minimum: {min(disk_values):.1f}%")
            print("=" * 50)
            
        except Exception as e:
            print(f"Error generating summary statistics: {e}")
