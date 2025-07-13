import argparse
import sys
import signal
import time
import threading
from datetime import datetime
from monitor import SystemMonitor
from visualizer import Visualizer
from logger import LogManager

class AutoSysMonitor:
    def __init__(self):
        self.monitor = SystemMonitor()
        self.visualizer = Visualizer()
        self.log_manager = LogManager()
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start the monitoring process"""
        if self.monitoring:
            print("Monitoring is already running!")
            return
            
        print("Starting AutoSysMonitor...")
        print("Press Ctrl+C to stop monitoring")
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Keep main thread alive
        try:
            while self.monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        if not self.monitoring:
            print("Monitoring is not running!")
            return
            
        print("\nStopping AutoSysMonitor...")
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("Monitoring stopped.")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get system metrics
                metrics = self.monitor.get_system_metrics()
                
                # Log metrics
                self.log_manager.log_metrics(metrics)
                
                # Check for alerts
                self.monitor.check_alerts(metrics)
                
                # Check if log rotation is needed
                self.log_manager.check_rotation()
                
                # Wait for next interval
                time.sleep(60)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def plot_usage(self, days=1):
        """Generate usage plots"""
        try:
            self.visualizer.plot_usage_trends(days)
            print(f"Usage plots generated for the last {days} day(s)")
        except Exception as e:
            print(f"Error generating plots: {e}")
    
    def rotate_logs(self):
        """Manually rotate logs"""
        try:
            self.log_manager.rotate_logs()
            print("Logs rotated successfully")
        except Exception as e:
            print(f"Error rotating logs: {e}")
    
    def show_status(self):
        """Show current system status"""
        try:
            metrics = self.monitor.get_system_metrics()
            print("\n=== Current System Status ===")
            print(f"CPU Usage: {metrics['cpu_percent']:.1f}%")
            print(f"RAM Usage: {metrics['memory_percent']:.1f}%")
            print(f"Disk Usage: {metrics['disk_percent']:.1f}%")
            print(f"Timestamp: {metrics['timestamp']}")
            print("==============================\n")
        except Exception as e:
            print(f"Error getting system status: {e}")

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\nReceived interrupt signal. Shutting down...")
    sys.exit(0)

def main():
    """Main function with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description="AutoSysMonitor - Linux System Resource Monitoring Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py start                    # Start monitoring
  python main.py plot                     # Generate usage plots
  python main.py plot --days 7           # Plot last 7 days
  python main.py rotate                   # Rotate logs manually
  python main.py status                   # Show current status
        """
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'plot', 'rotate', 'status'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=1,
        help='Number of days to plot (default: 1)'
    )
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create monitor instance
    monitor = AutoSysMonitor()
    
    # Execute commands
    if args.command == 'start':
        monitor.start_monitoring()
    elif args.command == 'plot':
        monitor.plot_usage(args.days)
    elif args.command == 'rotate':
        monitor.rotate_logs()
    elif args.command == 'status':
        monitor.show_status()

if __name__ == "__main__":
    main()
