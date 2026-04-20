import psutil
import docker
import requests
import time
import socket
import subprocess

# Backend settings
BACKEND_URL = "http://YOUR_BACKEND_IP:3000/api/metrics"
SERVER_NAME = socket.gethostname()

try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"Error connecting to Docker: {e}")
    docker_client = None

def get_system_metrics():
    """Collect core system metrics."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }

def get_system_logs(lines=15):
    """Fetch recent system log lines via journalctl."""
    try:
        # journalctl works well on Ubuntu, CentOS, and AlmaLinux.
        result = subprocess.run(
            ['journalctl', '-n', str(lines), '--no-pager'], 
            capture_output=True, 
            text=True
        )
        # Clean and convert output to a list of strings.
        return [line for line in result.stdout.split('\n') if line.strip()]
    except Exception as e:
        return [f"System log retrieval failed: {e}"]

def get_docker_data(log_lines=10):
    """Collect container status and recent logs."""
    if not docker_client:
        return []
    
    containers_data = []
    for container in docker_client.containers.list(all=True):
        # Attempt to fetch logs from each container.
        try:
            raw_logs = container.logs(tail=log_lines)
            # Decode bytes to string and ignore unsupported characters.
            logs = raw_logs.decode('utf-8', errors='ignore').strip().split('\n')
        except Exception as e:
            logs = [f"Could not read logs: {e}"]

        containers_data.append({
            "id": container.short_id,
            "name": container.name,
            "status": container.status,
            "image": container.image.tags[0] if container.image.tags else "unknown",
            "recent_logs": logs
        })
    return containers_data

def send_data_to_backend(payload):
    """Send payload data to the main API endpoint."""
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=5)
        print(f"[{time.strftime('%X')}] Data sent successfully. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[{time.strftime('%X')}] Failed to send data: {e}")

def main():
    print(f"Starting Linux Agent with Logs tracking on {SERVER_NAME}...")
    while True:
        sys_metrics = get_system_metrics()
        sys_logs = get_system_logs(lines=15) # Collect the latest 15 server log lines.
        docker_data = get_docker_data(log_lines=10) # Collect the latest 10 log lines per container.
        
        payload = {
            "server_name": SERVER_NAME,
            "system": sys_metrics,
            "system_logs": sys_logs,
            "containers": docker_data,
            "timestamp": time.time()
        }
        
        send_data_to_backend(payload)
        
        time.sleep(10)

if __name__ == "__main__":
    main()