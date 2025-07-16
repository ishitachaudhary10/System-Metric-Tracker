

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class LogManager:
    def __init__(self):
        self.log_file = "syslog.txt"
        self.alert_file = "alerts.txt"
        self.max_size = 1024 * 1024  # 1MB in bytes
        self.max_age = 3  # days
        
    def log_metrics(self, metrics):
        """
        Log system metrics to the main log file
        Args: metrics dict from SystemMonitor.get_system_metrics()
        """
        if not metrics:
            return
            
        try:
            log_entry = (
                f"{metrics['timestamp']} | "
                f"CPU: {metrics['cpu_percent']:.1f}% | "
                f"RAM: {metrics['memory_percent']:.1f}% | "
                f"Disk: {metrics['disk_percent']:.1f}%\n"
            )
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                f.flush()  # Ensure data is written immediately
                
        except Exception as e:
            print(f"Error logging metrics: {e}")
    
    def log_alert(self, alert_message):
        """
        Log alert message to alerts file
        Args: alert_message - string message to log
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} | {alert_message}\n"
            
            with open(self.alert_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                f.flush()
                
        except Exception as e:
            print(f"Error logging alert: {e}")
    
    def check_rotation(self):
        """
        Check if log rotation is needed based on file size or age
        """
        try:
            if self._needs_rotation():
                self.rotate_logs()
        except Exception as e:
            print(f"Error checking rotation: {e}")
    
    def _needs_rotation(self):
        """
        Check if log file needs rotation
        Returns: True if rotation is needed, False otherwise
        """
        if not os.path.exists(self.log_file):
            return False
            
        try:
            # Check file size
            file_size = os.path.getsize(self.log_file)
            if file_size > self.max_size:
                return True
            
            # Check file age
            file_mtime = os.path.getmtime(self.log_file)
            file_age = datetime.now() - datetime.fromtimestamp(file_mtime)
            if file_age.days >= self.max_age:
                return True
                
            return False
            
        except Exception as e:
            print(f"Error checking rotation needs: {e}")
            return False
    
    def rotate_logs(self):
        """
        Rotate log files by creating backups and starting new files
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Rotate main log file
            if os.path.exists(self.log_file):
                backup_name = f"syslog_backup_{timestamp}.txt"
                shutil.move(self.log_file, backup_name)
                
                # Compress the backup
                self._compress_file(backup_name)
                
                print(f"Log rotated: {backup_name} -> {backup_name}.gz")
            
            # Rotate alert log file if it exists
            if os.path.exists(self.alert_file):
                alert_backup_name = f"alerts_backup_{timestamp}.txt"
                shutil.move(self.alert_file, alert_backup_name)
                
                # Compress the backup
                self._compress_file(alert_backup_name)
                
                print(f"Alert log rotated: {alert_backup_name} -> {alert_backup_name}.gz")
                
        except Exception as e:
            print(f"Error rotating logs: {e}")
    
    def _compress_file(self, filename):
        """
        Compress a file using gzip
        Args: filename - path to file to compress
        """
        try:
            with open(filename, 'rb') as f_in:
                with gzip.open(f"{filename}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file after compression
            os.remove(filename)
            
        except Exception as e:
            print(f"Error compressing file {filename}: {e}")
    
    def read_log_data(self, days=1):
        """
        Read and parse log data from files
        Args: days - number of days to read back
        Returns: list of parsed log entries
        """
        data = []
        
        try:
            # Read current log file
            if os.path.exists(self.log_file):
                data.extend(self._parse_log_file(self.log_file, days))
            
            # Read backup files if needed
            backup_files = self._get_backup_files(days)
            for backup_file in backup_files:
                if backup_file.endswith('.gz'):
                    data.extend(self._parse_compressed_log_file(backup_file, days))
                else:
                    data.extend(self._parse_log_file(backup_file, days))
            
            # Sort by timestamp
            data.sort(key=lambda x: x['timestamp'])
            
            return data
            
        except Exception as e:
            print(f"Error reading log data: {e}")
            return []
    
    def _parse_log_file(self, filename, days):
        """
        Parse a log file and return entries within the specified days
        """
        entries = []
        cutoff_time = datetime.now() - timedelta(days=days)
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = self._parse_log_line(line.strip())
                    if entry and entry['timestamp'] >= cutoff_time:
                        entries.append(entry)
                        
        except Exception as e:
            print(f"Error parsing log file {filename}: {e}")
            
        return entries
    
    def _parse_compressed_log_file(self, filename, days):
        """
        Parse a compressed log file and return entries within the specified days
        """
        entries = []
        cutoff_time = datetime.now() - timedelta(days=days)
        
        try:
            with gzip.open(filename, 'rt', encoding='utf-8') as f:
                for line in f:
                    entry = self._parse_log_line(line.strip())
                    if entry and entry['timestamp'] >= cutoff_time:
                        entries.append(entry)
                        
        except Exception as e:
            print(f"Error parsing compressed log file {filename}: {e}")
            
        return entries
    
    def _parse_log_line(self, line):
        """
        Parse a single log line
        Returns: dict with parsed data or None if parsing fails
        """
        try:
            # Expected format: "2023-12-01 10:30:00 | CPU: 45.2% | RAM: 67.8% | Disk: 23.1%"
            parts = line.split(' | ')
            if len(parts) != 4:
                return None
                
            timestamp_str = parts[0]
            cpu_str = parts[1].replace('CPU: ', '').replace('%', '')
            ram_str = parts[2].replace('RAM: ', '').replace('%', '')
            disk_str = parts[3].replace('Disk: ', '').replace('%', '')
            
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            
            return {
                'timestamp': timestamp,
                'cpu_percent': float(cpu_str),
                'memory_percent': float(ram_str),
                'disk_percent': float(disk_str)
            }
            
        except Exception as e:
            print(f"Error parsing log line '{line}': {e}")
            return None
    
    def _get_backup_files(self, days):
        """
        Get list of backup files within the specified days
        """
        backup_files = []
        cutoff_time = datetime.now() - timedelta(days=days)
        
        try:
            for file in os.listdir('.'):
                if file.startswith('syslog_backup_') and (file.endswith('.txt') or file.endswith('.gz')):
                    file_mtime = os.path.getmtime(file)
                    if datetime.fromtimestamp(file_mtime) >= cutoff_time:
                        backup_files.append(file)
                        
        except Exception as e:
            print(f"Error getting backup files: {e}")
            
        return sorted(backup_files)
