import os
import subprocess
import getpass
import argparse
from pathlib import Path
from dotenv import load_dotenv

__version__ = "0.1.1-dev"


load_dotenv()

SWARM_TOKEN_FILE = Path.home() / ".logninja_swarm_token"
HOSTS_FILE = "/etc/hosts"

HOST_ENTRIES = {
    "batcave": os.getenv("ALIAS_batcave"),
    "pennyworth": os.getenv("ALIAS_pennyworth"),
    "waynemanor": os.getenv("ALIAS_waynemanor"),
}


def banner():
    print("🛡️  LOGGIE - Secure Logging Infrastructure")
    print("👤  Creator: loggie.eth")
    print("🔗  https://etherscan.io/address/0xF62E1F6193FD0b3d8eD7B3198915D3b0c9bd3f99")
    print(f"🧩  Version: {__version__}\n")

def run(cmd, use_sudo=False):
    if use_sudo and os.geteuid() != 0:
        cmd = f"sudo {cmd}"
    print(f"▶️ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def get_swarm_join_command():
    try:
        result = subprocess.check_output("docker swarm join-token -q worker", shell=True, text=True)
        return result.strip()
    except subprocess.CalledProcessError:
        return None

def write_token(token):
    SWARM_TOKEN_FILE.write_text(token)
    print(f"🔑 Swarm token saved to {SWARM_TOKEN_FILE}")

def read_token():
    if SWARM_TOKEN_FILE.exists():
        return SWARM_TOKEN_FILE.read_text().strip()
    return None

def prompt_swarm_mode():
    mode = input("🧭 Is this node a [m]anager or [w]orker? (m/w): ").lower().strip()
    return 'manager' if mode == 'm' else 'worker'

def sync_hosts():
    print("🔁 Syncing /etc/hosts with trusted node aliases...")
    lines_to_add = [f"{ip} {name}\n" for name, ip in HOST_ENTRIES.items()]
    existing = Path(HOSTS_FILE).read_text()
    with open("/tmp/hosts.tmp", "w") as temp:
        for line in lines_to_add:
            if line not in existing:
                temp.write(line)
    run(f"sudo cat /tmp/hosts.tmp | sudo tee -a {HOSTS_FILE} > /dev/null && rm /tmp/hosts.tmp")
    print("✅ /etc/hosts updated!")

def setup_node(sync=False):
    print("🛠 Updating system and installing dependencies...")
    run("apt update && apt upgrade -y", use_sudo=True)
    run("apt install -y apt-transport-https ca-certificates curl software-properties-common git", use_sudo=True)

    print("🐳 Installing Docker...")
    run("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor | tee /etc/apt/trusted.gpg.d/docker.gpg > /dev/null", use_sudo=True)
    run('sh -c "echo \"deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" > /etc/apt/sources.list.d/docker.list"', use_sudo=True)
    run("apt update && apt install -y docker-ce docker-ce-cli containerd.io", use_sudo=True)

    print("🔁 Enabling Docker service...")
    run("systemctl enable docker && systemctl start docker", use_sudo=True)

    print("👥 Adding current user to docker group...")
    run(f"usermod -aG docker {getpass.getuser()}", use_sudo=True)

    print("📦 Installing Docker Compose Plugin...")
    run("apt install -y docker-compose-plugin", use_sudo=True)

    print("💻 Setting up Swarm...")
    try:
        subprocess.run("docker swarm init", shell=True, check=True)
        token = get_swarm_join_command()
        if token:
            write_token(token)
    except subprocess.CalledProcessError:
        print("⚠️  Could not init swarm. Trying join instead...")
        token = read_token()
        if token:
            manager_ip = input("🔌 Enter IP address of swarm manager: ").strip()
            run(f"docker swarm join --token {token} {manager_ip}:2377")
        else:
            print("❌ No token found to join swarm. Please init a manager first.")

    print("📁 Cloning base AI container examples...")
    run("git clone https://github.com/docker/getting-started ~/docker-getting-started || true")

    if sync:
        sync_hosts()

    print("✅ Node setup complete! Reboot recommended.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--credits', action='store_true', help='Show LOGGIE creator info')
    parser.add_argument('--sync-hosts', action='store_true', help='Sync /etc/hosts with node names')
    args = parser.parse_args()

    if args.credits:
        banner()
    else:
        banner()
        setup_node(sync=args.sync_hosts)
