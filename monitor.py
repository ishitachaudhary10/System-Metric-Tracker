import psutil
import time
from datetime import datetime
from logger import LogManager

class SystemMonitor:
    def __init__(self):
        self.log_manager = LogManager()
        self.cpu_threshold = 80.0  # CPU usage threshold for alerts
        
    def get_system_metrics(self):
        """
        Collect current system metrics
        Returns: dict with CPU, memory, disk usage and timestamp
        """
        try:
            # Get CPU usage (average over 1 second)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get disk usage for root partition
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'timestamp': timestamp
            }
            
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            return None
    
    def check_alerts(self, metrics):
        """
        Check if any metrics exceed thresholds and generate alerts
        Args: metrics dict from get_system_metrics()
        """
        if not metrics:
            return
            
        try:
            # Check CPU usage threshold
            if metrics['cpu_percent'] > self.cpu_threshold:
                alert_message = (
                    f"HIGH CPU USAGE ALERT: {metrics['cpu_percent']:.1f}% "
                    f"at {metrics['timestamp']}"
                )
                
                # Print warning to console
                print(f"⚠️  {alert_message}")
                
                # Log alert to alerts.txt
                self.log_manager.log_alert(alert_message)
                
        except Exception as e:
            print(f"Error checking alerts: {e}")
    
    def get_process_info(self, limit=5):
        """
        Get top processes by CPU usage
        Args: limit - number of processes to return
        Returns: list of process info dictionaries
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] is not None:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and return top processes
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:limit]
            
        except Exception as e:
            print(f"Error getting process info: {e}")
            return []
    
    def get_system_info(self):
        """
        Get general system information
        Returns: dict with system info
        """
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'boot_time': boot_time.strftime("%Y-%m-%d %H:%M:%S"),
                'uptime': str(uptime).split('.')[0],  # Remove microseconds
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'total_memory': psutil.virtual_memory().total,
                'total_disk': psutil.disk_usage('/').total
            }
            
        except Exception as e:
            print(f"Error getting system info: {e}")
            return {}
