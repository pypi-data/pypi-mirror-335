from . import display
import urllib.request
import urllib.error
from pathlib import Path
import subprocess
import os
import platform


def install(update,force):
    
    if update:
        docker_update(force)
    else:
        docker_install(force)


def docker_get_version():
    # fetch updates
    command = [
        "docker",
        "-v",
    ]
    display.print_debug("Checking Docker Version...")
    result = subprocess.run(command, capture_output=True)

    if result.returncode == 0:
        return result.stdout.decode().strip()
    else:
        return None


def docker_install(force):
    display.print_log("Installing Docker...")
    existing_version = docker_get_version()
    os_env = detect_os_env()

    if existing_version:
        display.print_complete(f"Docker already installed ({existing_version})")
        if not force:
            return

    if os_env["os_id"] in ["debian", "ubuntu"]:
        install_via_apt(os_env, force)
    else:
        display.print_error(
            f"This operating configuration isn't currenly supported. Please contact the Shoestring team for support and provide them with these details:\n{os_env}"
        )

def docker_update(force):
    display.print_log("Updating Docker...")
    os_env = detect_os_env()

    if os_env["os_id"] in ["debian", "ubuntu"]:
        update_via_apt(os_env, force)
    else:
        display.print_error(
            f"This operating configuration isn't currenly supported. Please contact the Shoestring team for support and provide them with these details:\n{os_env}"
        )

def install_via_apt(os_env, force):
    docker_set_up_apt_source(os_env,force)

    # for install
    subprocess_exec(
        "Install docker",
        [
            "apt-get",
            "install",
            "docker-ce",
            "docker-ce-cli",
            "containerd.io",
            "docker-buildx-plugin",
            "docker-compose-plugin",
        ],
    )

    subprocess_exec("Create docker permissions group", ["groupadd", "docker", "-f"])
    subprocess_exec(
        "Let the user account run Docker without elevated privileges by adding user to permissions group",
        "usermod -a -G docker $USER",
    )
    # subprocess_exec(None,["newgrp","docker"])
    subprocess_exec(
        "Start Docker in the background", ["systemctl", "start", "docker"]
    )
    subprocess_exec(
        "Set Docker to run in the background whenever the system boots up",
        ["systemctl", "enable", "docker"],
    )

    installed_version = docker_get_version()
    if installed_version:
        display.print_complete(f"Docker installed ({installed_version})")
    else:
        display.print_error(f"Docker installation failed!")

    # Prompt to restart


def update_via_apt(os_env,force):
    subprocess_exec(
        "Update docker",
        [
            "apt-get",
            "install",
            "docker-ce",
            "docker-ce-cli",
            "containerd.io",
            "docker-buildx-plugin",
            "docker-compose-plugin",
        ],
    )

    installed_version = docker_get_version()
    if installed_version:
        display.print_complete(f"Complete: {installed_version}")
    else:
        display.print_error(f"Docker update failed!")


def docker_set_up_apt_source(os_env, force):
    apt_source_file = Path("/etc/apt/sources.list.d/docker.list")

    if apt_source_file.exists():
        display.print_complete("APT source already set up")
        if not force:
            return

    display.print_log("Setting up docker apt source...")

    subprocess_exec("Update apt index", ["apt-get", "update"])
    subprocess_exec(
        "Ensure https certificates are installed and up-to-date",
        ["apt-get", "install", "ca-certificates"],
    )

    keyring_dir = Path("/etc/apt/keyrings")

    keyring_dir.mkdir(mode=0o755, parents=True, exist_ok=True)

    keyring_file = keyring_dir / "docker.asc"

    try:
        keyring_file.touch(mode=0o644, exist_ok=True)
    except PermissionError:
        display.print_error(
            f"Elevated permissions required to write to the {keyring_file} file.\nPlease run with sudo."
        )

    URL_SET = {
        "debian": "https://download.docker.com/linux/debian",
        "ubuntu": "https://download.docker.com/linux/ubuntu",
    }

    base_url = URL_SET[os_env["os_id"]]
    try:
        with urllib.request.urlopen(f"{base_url}/gpg") as web_in:
            keyring = web_in.read()
    except urllib.error.HTTPError:
        display.print_error("Failed to Fetch Docker keyring certificate")
        return False

    try:
        with open(keyring_file, "wb") as f_out:
            f_out.write(keyring)
        display.print_complete("Downloaded keyring file")
    except PermissionError:
        display.print_error(
            f"Elevated permissions required to write to the {keyring_file} file.\nPlease run with sudo."
        )

    outcome = subprocess.run(["dpkg", "--print-architecture"], capture_output=True)
    architecture = outcome.stdout.decode().strip()

    source_desc = f'deb [arch={architecture} signed-by=/etc/apt/keyrings/docker.asc] {base_url} {os_env["codename"]} stable'
    with open(apt_source_file, "w") as f:
        f.write(source_desc)
    display.print_complete("Created apt source file")

    subprocess_exec("Update apt index", ["apt-get", "update"])
    display.print_complete("Apt source set up for docker")


def subprocess_exec(label, command):
    result = subprocess.run(
        command, capture_output=True, shell=isinstance(command,str)
    )
    if result.returncode != 0:
        display.print_error(result.stderr.decode().strip())
    elif label:
        display.print_complete(label)


def detect_os_env():
    os_env = {}
    os_env["system"] = platform.system()
    if os_env["system"] == "Linux":
        os_release = platform.freedesktop_os_release()
        os_env["os_id"] = os_release["ID"]
        os_env["codename"] = os_release.get(
            "UBUNTU_CODENAME", os_release.get("VERSION_CODENAME")
        )

    display.print_debug(os_env)
    return os_env
