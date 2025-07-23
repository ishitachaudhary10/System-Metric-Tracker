import os
import sys
import psutil
from datetime import datetime
from pathlib import Path

def check_dependencies():
    """
    Check if all required dependencies are available
    Returns: True if all dependencies are available, False otherwise
    """
    try:
        import psutil
        import matplotlib.pyplot as plt
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install psutil matplotlib")
        return False

def format_bytes(bytes_value):
    
    if bytes_value == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while bytes_value >= 1024 and i < len(size_names) - 1:
        bytes_value /= 1024.0
        i += 1
    
    return f"{bytes_value:.1f} {size_names[i]}"

def get_system_uptime():

    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        return ", ".join(parts) if parts else "Less than a minute"
        
    except Exception as e:
        return f"Error getting uptime: {e}"

def check_disk_space(path="/"):
  
    try:
        disk_usage = psutil.disk_usage(path)
        return {
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free,
            'percent': (disk_usage.used / disk_usage.total) * 100,
            'total_formatted': format_bytes(disk_usage.total),
            'used_formatted': format_bytes(disk_usage.used),
            'free_formatted': format_bytes(disk_usage.free)
        }
    except Exception as e:
        return {'error': str(e)}

def get_memory_info():
    """
    Get detailed memory information
    Returns: dict with memory info
    """
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'total_formatted': format_bytes(memory.total),
            'available_formatted': format_bytes(memory.available),
            'used_formatted': format_bytes(memory.used),
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent,
            'swap_total_formatted': format_bytes(swap.total),
            'swap_used_formatted': format_bytes(swap.used)
        }
    except Exception as e:
        return {'error': str(e)}

def get_cpu_info():
    
    try:
        cpu_freq = psutil.cpu_freq()
        cpu_times = psutil.cpu_times()
        
        return {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'current_freq': cpu_freq.current if cpu_freq else None,
            'min_freq': cpu_freq.min if cpu_freq else None,
            'max_freq': cpu_freq.max if cpu_freq else None,
            'cpu_times': {
                'user': cpu_times.user,
                'system': cpu_times.system,
                'idle': cpu_times.idle
            }
        }
    except Exception as e:
        return {'error': str(e)}

def validate_file_permissions(file_path):
    
    try:
        path = Path(file_path)
        parent_dir = path.parent
        
        return {
            'exists': path.exists(),
            'readable': path.is_file() and os.access(path, os.R_OK) if path.exists() else False,
            'writable': path.is_file() and os.access(path, os.W_OK) if path.exists() else False,
            'parent_writable': os.access(parent_dir, os.W_OK) if parent_dir.exists() else False,
            'parent_exists': parent_dir.exists()
        }
    except Exception as e:
        return {'error': str(e)}

def cleanup_old_files(pattern, max_age_days=30):
   
    deleted_files = []
    cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
    
    try:
        for file in os.listdir('.'):
            if pattern in file:
                file_mtime = os.path.getmtime(file)
                if file_mtime < cutoff_time:
                    os.remove(file)
                    deleted_files.append(file)
                    
    except Exception as e:
        print(f"Error cleaning up old files: {e}")
        
    return deleted_files

def print_system_info():
    
    print("\n=== System Information ===")
    
    # Basic system info
    print(f"System: {os.name}")
    print(f"Python Version: {sys.version}")
    print(f"Uptime: {get_system_uptime()}")
    
    # CPU info
    cpu_info = get_cpu_info()
    if 'error' not in cpu_info:
        print(f"CPU Cores: {cpu_info['physical_cores']} physical, {cpu_info['logical_cores']} logical")
        if cpu_info['current_freq']:
            print(f"CPU Frequency: {cpu_info['current_freq']:.0f} MHz")
    
    # Memory info
    memory_info = get_memory_info()
    if 'error' not in memory_info:
        print(f"Total RAM: {memory_info['total_formatted']}")
        print(f"Available RAM: {memory_info['available_formatted']}")
        if memory_info['swap_total'] > 0:
            print(f"Swap: {memory_info['swap_total_formatted']}")
    
    # Disk info
    disk_info = check_disk_space()
    if 'error' not in disk_info:
        print(f"Disk Space: {disk_info['used_formatted']} / {disk_info['total_formatted']} ({disk_info['percent']:.1f}%)")
    
    print("=" * 30)
