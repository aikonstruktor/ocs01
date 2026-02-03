import socket, subprocess, sys, os

def check_hostname_resolution():
    h = socket.gethostname()
    ip = None
    
    # getent first
    out = subprocess.run(
        ['getent', 'hosts', h],
        capture_output=True,
        text=True
    ).stdout.split()
    
    if out:
        ip = out[0]
    
    # /etc/hosts fallback
    if not ip and os.path.exists('/etc/hosts'):
        with open('/etc/hosts') as f:
            for line in f:
                if line.strip().startswith('#'):
                    continue
                parts = line.split()
                if parts and parts[0][0].isdigit() and h in parts[1:]:
                    ip = parts[0]
                    break
    
    if not ip:
        sys.exit(f"ERROR: unable to resolve hostname '{h}'")
    
    if ip.startswith('127.') or ip == '::1':
        sys.exit(f"ERROR: hostname '{h}' resolves to loopback ({ip})")
    
    print(f'OK: {h} -> {ip}')

