import os
import subprocess
import getpass
import argparse

__version__ = "v0.1.0-dev"

def banner():
    print("🛡️  LOGGIE - Secure Logging Infrastructure")
    print("👤  Creator: loggie.eth")
    print("🔗  https://etherscan.io/address/0xF62E1F6193FD0b3d8eD7B3198915D3b0c9bd3f99")
    print(f"🧩  Version: {__version__}\n")

def run(cmd):
    print(f"▶️ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def setup_node():
    print("🛠 Updating system and installing dependencies...")
    run("sudo apt update && sudo apt upgrade -y")
    run("sudo apt install -y apt-transport-https ca-certificates curl software-properties-common git")

    print("🐳 Installing Docker...")
    run("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/docker.gpg")
    run('echo "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list')
    run("sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io")

    print("🔁 Enabling Docker service...")
    run("sudo systemctl enable docker && sudo systemctl start docker")

    print("👥 Adding current user to docker group...")
    run(f"sudo usermod -aG docker {getpass.getuser()}")

    print("📦 Installing Docker Compose Plugin...")
    run("sudo apt install -y docker-compose-plugin")

    print("💻 Setting up Swarm (you'll be prompted to init or join later)...")
    run("docker swarm init || echo 'Skipping init, likely a worker node. Use docker swarm join manually.'")

    print("📁 Cloning base AI container examples...")
    run("git clone https://github.com/docker/getting-started ~/docker-getting-started || true")

    print("✅ Node setup complete! Reboot recommended.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--credits', action='store_true', help='Show LOGGIE creator info')
    args = parser.parse_args()

    if args.credits:
        banner()
    else:
        banner()
        setup_node()
