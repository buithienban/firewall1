import subprocess
import requests

GITHUB_RAW_URL = "https://raw.githubusercontent.com/buithienban/hiddenips/main/ipsfastvnteam.txt"

def check_if_ipset_installed():
    try:
        subprocess.check_output(["sudo", "ipset", "list"], stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def check_if_iptables_installed():
    try:
        subprocess.check_output(["sudo", "iptables", "-L"], stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def create_ipset_blacklist():
    subprocess.run(
        ["sudo", "ipset", "create", "fastvnteam-blacklist", "hash:ip", "hashsize", "8192"]
    )


def add_ip_to_blacklist(ip):
    subprocess.run(["sudo", "ipset", "add", "fastvnteam-blacklist", ip])


def block_ipset_blacklist():
    subprocess.run(
        [
            "sudo",
            "iptables",
            "-I",
            "INPUT",
            "-m",
            "set",
            "--match-set",
            "fastvnteam-blacklist",
            "src",
            "-j",
            "DROP",
        ]
    )

def block_ip(ip):
    subprocess.run(["sudo", "iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"])


def get_scanners_ips():
    try:
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            content = response.text.split("\n")
            scanners_ips = set()
            for line in content:
                line = line.split('#', 1)[0].strip()
                if line and not line.startswith("#"):
                    ip = line.split()[0]
                    scanners_ips.add(ip)
            return scanners_ips
    except Exception as e:
        print(f"Error fetching IP list: {e}")
        return set()


def block_scanners_ips():
    confirmation = input(
        "Chức năng chặn tìm kiếm địa chỉ ip server sẽ tự động tải xuống từ repo https://github.com/buithienban/. Bạn muốn tiếp tục chứ? (y/n): "
    )

    if confirmation.lower() not in ["y", "yes"]:
        print("Đã thoát.")
        return

    print("Hãy đợi chút... (có thể mất từ 1-2 phút)")
    scanners_ips = get_scanners_ips()

    create_ipset_blacklist()

    for ip in scanners_ips:
        add_ip_to_blacklist(ip)

    block_ipset_blacklist()

    print("")
    print("Đã bật firewall thành công.")
    print("FASTVNTEAM trân trọng cảm ơn đại diện Bùi Thiện Bản.")
    print("")


def uninstall_fastvnteam():
    confirmation = input("Bạn có chắc chắn muốn gỡ bỏ FIREWALLFASTVNTEAM không? (y/n): ")

    if confirmation.lower() not in ["y", "yes"]:
        print("Đã thoát.")
        return

    subprocess.run(
        [
            "sudo",
            "iptables",
            "-D",
            "INPUT",
            "-m",
            "set",
            "--match-set",
            "fastvnteam-blacklist",
            "src",
            "-j",
            "DROP",
        ]
    )
    subprocess.run(["sudo", "ipset", "flush", "fastvnteam-blacklist"])
    subprocess.run(["sudo", "ipset", "destroy", "fastvnteam-blacklist"])
    subprocess.run(["sudo", "ipset", "destroy", "fastvnteam-blacklist"])

    print("Đã gỡ bỏ FASTVNTEAM.")
    print("")


def main():
    if not check_if_ipset_installed():
        print(
            "**ipset** chưa được cài đặt. Vui lòng cài đặt **ipset** và chạy lại script."
        )
        return

    if not check_if_iptables_installed():
        print(
            "**iptables** chưa được cài đặt. Vui lòng cài đặt **iptables** và chạy lại script."
        )
        return

    print(
        "Cảnh báo: firewall này được FASTVNTEAM phát triển miễn phí chỉ chặn khoảng 90% nếu muốn mua phiên bản hoàn thiện nhất hãy liên hệ https://t.me/buithienban."
    )
    print(
        "Tuy nhiên, do script sử dụng iptables và ipset, bạn hãy chắc chắn rằng mình đã có một bản backup rules iptables để có thể revert lại nếu như script gây ra trục trặc. Cũng như, hãy đảm bảo rằng bạn đã cài đặt iptables, ipset và requests (pip install requests/pip3 install requests) để có thể sử dụng."
    )
    print("")
    print("FW SPONSORED FASTVNTEAM")
    print("")
    confirmation = input("Bạn có chắc chắn muốn tiếp tục không? (y/n): ")

    if confirmation.lower() not in ["y", "yes", "ok"]:
        print("Đã thoát.")
        return

    print(" ")
    print("--------------- MENU --------------")
    print(" ")
    print("1. ON FIREWALL FASTVNTEAM")
    print("2. Gỡ bỏ FIREWALL FASTVNTEAM")
    print(" ")
    print("-----------------------------------")
    print(" ")
    choice = input("Chọn chức năng: ")

    if choice == "1":
        block_scanners_ips()
    elif choice == "2":
        uninstall_fastvnteam()
    else:
        print("Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    main()
