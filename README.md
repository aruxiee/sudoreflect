
# sudoreflect: Credential Harvester for Sudo
Post-exploitation tool for **unelevated shells**. Exploits Linux environment precedence to intercept `sudo` authentication attempts. Captures cleartext passwords by masquerading as the legitimate `sudo` binary.

⚠️ **Please Note:** This project is strictly for **Educational and Authorized Penetration Testing**. I am not responsible for any of the shenanigans you guys pull.

---

## 📂 How it Works
The script leverages the **`$PATH` Environment Variable**. When a user executes a command, the shell searches directories in `$PATH` from left to right. `sudoreflect` injects a user-controlled directory at the very top of this list.

- **Interception**: When the user types `sudo`, the shell hits the fake script in `~/.local/bin/` instead of the real one in `/usr/bin/`.
- **Validation**: The script prompts for a password. To maintain stealth, it validates this password against the real `sudo -v` in the background.
- **Capture**: If valid, the password is saved to a hidden log file.
- **Reflective Execution**: The script then passes the password and original arguments to the real `sudo` so the user's command executes successfully without suspicion.

---

## 🚀 Deployment
The console automates the entire attack and cleanup chain.

*   **Identification**: Automatically detects if the environment is running `Bash` or `Zsh` to target the correct config file (`.bashrc` or `.zshrc`).
*   **Setup**: Creates hidden directories (`~/.local/bin` and `~/.local/.cache`) to keep the payload and captured logs.
*   **Persistence**: Injects the path override into the shell config. This makes sure that the harvester activates every time the user opens a terminal, even after a **system reboot**.
*   **Self-Cleaning**: Once a successful capture occurs, the payload removes its own entry from the shell config, uninstalling itself to minimize forensic footprint.

---

## 🛠️ Execution Steps
- **Deploy the Harvester**:
    `python3 sudoreflect.py --deploy`
- **Activate Environment**:
    `source ~/.zshrc` (or just wait for the user to open a new terminal).
- **Retrieve Creds**:
    `cat ~/.local/.cache/sys_log.txt`
- **Manual Cleanup**:
    `python3 sudoreflect.py --revert`

---

## 💥 Impact & Use Cases
*   **Privilege Escalation**: Provides a direct path from a standard user to `root` by harvesting admin credentials.
*   **Lateral Movement**: Captured passwords often work across other machines in the same network/domain.
*   **Persistence Test**: Demonstrates a foothold that survives reboots.

---

## 🗺️ MITRE
| Technique ID | Name | Description |
| :--- | :--- | :--- |
| **T1546.004** | Event Triggered Execution: Unix Shell Configuration Modification | Modifying `.bashrc` or `.zshrc` to trigger the harvester. |
| **T1574.007** | Hijack Execution Flow: Path Interception | Placing a malicious binary in `$PATH` directory. |
| **T1056.001** | Input Capture: Keylogging | Intercepting creds via a fake CLI prompt. |

---

## 🔧 Tweaks
*   **Exfiltration**: You can add a `webhook` or `curl` command within the `cleanup()` function to send the password to a remote server.
*   **Multi-User Targets**: If write access is available to `/etc/skel`, the hijack can be pre-installed for every *new* user created on the system.
*   **Dynamic Prompting**: You can adjust the script to detect the user's locale and display the `[sudo] password for...` prompt in different languages (e.g. French, German, Hindi) for compatibility.

---
