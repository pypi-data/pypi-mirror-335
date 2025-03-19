# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module for creating custom environments.

"""
import base64
import binascii
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union

from jupyter_client.kernelspec import KernelSpecManager

from qbraid_core.system.generic import replace_str
from qbraid_core.system.packages import set_include_sys_site_pkgs_value

from .state import update_state_json

logger = logging.getLogger(__name__)


def create_local_venv(
    slug_path: Union[str, Path], prompt: str, python_exe: Optional[Union[str, Path]] = None
) -> None:
    """Create virtual environment and swap PS1 display name."""
    try:
        # Ensure slug_path is a Path object
        slug_path = Path(slug_path)
        venv_path = slug_path / "pyenv"
        python_exe = Path(python_exe or sys.executable)
        subprocess.run([str(python_exe), "-m", "venv", str(venv_path)], check=True)

        # Determine the correct directory for activation scripts based on the operating system
        if sys.platform == "win32":
            scripts_path = venv_path / "Scripts"
            activate_files = ["activate.bat", "Activate.ps1"]
        else:
            scripts_path = venv_path / "bin"
            activate_files = ["activate", "activate.csh", "activate.fish"]

        for file in activate_files:
            file_path = scripts_path / file
            if file_path.exists():
                replace_str("(pyenv)", f"({prompt})", str(file_path))

        set_include_sys_site_pkgs_value(True, venv_path / "pyvenv.cfg")
        update_state_json(slug_path, 1, 1)
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("Error creating virtual environment: %s", err)
        update_state_json(slug_path, 1, 0, message=str(err))


# pylint: disable-next=too-many-locals
def create_qbraid_env_assets(
    slug: str,
    alias: Optional[str],
    kernel_name: str,
    slug_path: str,
    image_data_url: Optional[str] = None,
) -> None:
    """Create a qBraid environment including python venv, PS1 configs,
    kernel resource files, and qBraid state.json."""
    local_resource_dir = os.path.join(slug_path, "kernels", f"python3_{slug}")
    os.makedirs(local_resource_dir, exist_ok=True)

    # create state.json
    update_state_json(slug_path, 0, 0, env_name=alias)

    # create kernel.json
    kernel_json_path = os.path.join(local_resource_dir, "kernel.json")
    kernel_spec_manager = KernelSpecManager()
    kernelspec_dict = kernel_spec_manager.get_all_specs()
    kernel_data = kernelspec_dict["python3"]["spec"]
    if sys.platform == "win32":
        python_exec_path = os.path.join(slug_path, "pyenv", "Scripts", "python.exe")
    else:
        python_exec_path = os.path.join(slug_path, "pyenv", "bin", "python")
    kernel_data["argv"][0] = python_exec_path
    kernel_data["display_name"] = kernel_name
    with open(kernel_json_path, "w", encoding="utf-8") as file:
        json.dump(kernel_data, file, indent=4)

    # copy logo files
    if image_data_url:
        save_image_from_data_url(image_data_url, os.path.join(local_resource_dir, "logo-64x64.png"))
    else:
        sys_resource_dir = kernelspec_dict["python3"]["resource_dir"]
        logo_files = ["logo-32x32.png", "logo-64x64.png", "logo-svg.svg"]
        for file_name in logo_files:
            sys_path = os.path.join(sys_resource_dir, file_name)
            loc_path = os.path.join(local_resource_dir, file_name)
            if os.path.isfile(sys_path):
                shutil.copy(sys_path, loc_path)


def save_image_from_data_url(data_url: str, output_path: str) -> None:
    """Save an image from a base64-encoded Data URL to a file."""
    # Extract base64 content from the Data URL
    match = re.search(r"base64,(.*)", data_url)
    if not match:
        raise ValueError("Invalid Data URL")

    try:
        image_data = base64.b64decode(match.group(1))
    except binascii.Error as err:
        raise ValueError("Invalid Data URL") from err

    # Ensure the output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Write the image data to a file
    with open(output_path, "wb") as file:
        file.write(image_data)
