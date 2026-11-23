"""Where manimgx draws: on the CPU by default, on GPUs only when they are named.

manimgx draws with wgpu over Vulkan, and bundles Mesa's lavapipe: when the Vulkan loader
finds no driver at all, manimgx draws on the CPU. So a CPU process gets a driver list that
names no driver (``VK_ICD_FILENAMES``), and the GPUs are never opened. ``LP_NUM_THREADS`` sets
how many cores each worker's rasterizer uses.

GPUs are used only when named (``render.py --gpus 3,4``). On a machine with several identical
NVIDIA GPUs, NVIDIA's driver ignores ``CUDA_VISIBLE_DEVICES`` and wgpu always takes GPU 0, so
a small Vulkan layer (``vulkan/select_gpu.c``) shows each GPU worker only the GPU on its PCI
bus.

Every worker checks where it landed (``check_adapter``): a CPU worker on a GPU, or a GPU
worker on the CPU, fails instead of rendering.
"""

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from manimgx import _engine

from explain.paths import SKILL_ROOT

LAYER_NAME = "VK_LAYER_EXPLAIN_select_gpu"
LAYER_SOURCE = SKILL_ROOT / "vulkan" / "select_gpu.c"
LAYER_BUILD = SKILL_ROOT / "vulkan" / "build"
NO_DRIVER = LAYER_BUILD / "no_driver.json"
GPU_VARIABLES = ("VK_LAYER_PATH", "VK_INSTANCE_LAYERS", "EXPLAIN_VK_PCI_BUS", "CUDA_VISIBLE_DEVICES")
DEFAULT_THREADS = 8


@dataclass(frozen=True)
class Gpu:
    """One NVIDIA GPU as ``nvidia-smi`` lists it."""

    index: int
    bus: str


@dataclass(frozen=True)
class Device:
    """Where one process draws: the CPU with some threads, or one GPU.

    Attributes:
        gpu: The GPU, or None for the CPU.
        threads: Rasterizer threads on the CPU (ignored on a GPU).
    """

    gpu: Gpu | None = None
    threads: int = DEFAULT_THREADS

    @property
    def label(self) -> str:
        """``GPU 3`` or ``CPU ×8``, for logs and reports."""
        return f"GPU {self.gpu.index}" if self.gpu else f"CPU ×{self.threads}"


def named_gpus(indices: list[int]) -> list[Gpu]:
    """Look up GPUs by their ``nvidia-smi`` index.

    Args:
        indices: The indices the user named.

    Returns:
        The GPUs, in the order named.

    Raises:
        ValueError: If ``nvidia-smi`` is missing or an index does not exist.
    """
    if shutil.which("nvidia-smi") is None:
        raise ValueError("GPUs were named but nvidia-smi is not installed")
    out = subprocess.run(["nvidia-smi", "--query-gpu=index,pci.bus_id", "--format=csv,noheader"],
                         capture_output=True, text=True, check=True).stdout
    found = {}
    for line in out.strip().splitlines():
        index, bus_id = (field.strip() for field in line.split(","))
        found[int(index)] = Gpu(int(index), bus_id.split(":")[1].lower())
    missing = [i for i in indices if i not in found]
    if missing:
        raise ValueError(f"No GPU with index {missing}; have {sorted(found)}")
    return [found[i] for i in indices]


def layer_dir() -> Path:
    """Build the GPU-selection layer and its manifest once, and return their directory.

    Returns:
        The directory to put on ``VK_LAYER_PATH``.

    Raises:
        subprocess.CalledProcessError: If gcc cannot build the layer (Vulkan headers missing).
    """
    library = LAYER_BUILD / "libexplain_select_gpu.so"
    if not library.is_file() or library.stat().st_mtime < LAYER_SOURCE.stat().st_mtime:
        LAYER_BUILD.mkdir(parents=True, exist_ok=True)
        subprocess.run(["gcc", "-O2", "-shared", "-fPIC", "-fvisibility=hidden", "-o", str(library),
                        str(LAYER_SOURCE)], check=True)
        (LAYER_BUILD / "explain_select_gpu.json").write_text(json.dumps({
            "file_format_version": "1.1.2",
            "layer": {"name": LAYER_NAME, "type": "GLOBAL", "library_path": str(library),
                      "api_version": "1.3.242", "implementation_version": "1",
                      "description": "Expose only the physical device on PCI bus $EXPLAIN_VK_PCI_BUS"},
        }, indent=1))
    return LAYER_BUILD


def device_env(device: Device) -> dict[str, str]:
    """The environment for a process that draws on one device.

    Args:
        device: The CPU (with its threads) or one GPU.

    Returns:
        A copy of the current environment. For the CPU: the Vulkan loader sees no driver
        (``NO_DRIVER`` is never created), so manimgx falls back to its bundled lavapipe, and
        the GPU variables are removed. For a GPU: the selection layer is on and pinned to the
        GPU's PCI bus.
    """
    env = dict(os.environ)
    if device.gpu is None:
        for name in GPU_VARIABLES:
            env.pop(name, None)
        env.update({"VK_ICD_FILENAMES": str(NO_DRIVER), "VK_DRIVER_FILES": str(NO_DRIVER),
                    "LP_NUM_THREADS": str(device.threads), "EXPLAIN_DEVICE": "cpu"})
    else:
        for name in ("VK_ICD_FILENAMES", "VK_DRIVER_FILES", "LP_NUM_THREADS"):
            env.pop(name, None)
        env.update({"VK_LAYER_PATH": str(layer_dir()), "VK_INSTANCE_LAYERS": LAYER_NAME,
                    "EXPLAIN_VK_PCI_BUS": device.gpu.bus, "CUDA_VISIBLE_DEVICES": str(device.gpu.index),
                    "EXPLAIN_DEVICE": f"gpu:{device.gpu.index}"})
    return env


def check_adapter() -> str:
    """Fail unless manimgx is drawing where this process was sent.

    Returns:
        ``"<name> (<backend>)"`` of the adapter manimgx uses.

    Raises:
        RuntimeError: If the process was sent to the CPU but manimgx is on a GPU, or to a GPU
            but manimgx is on the CPU, or ``EXPLAIN_DEVICE`` is not set.
    """
    sent = os.environ.get("EXPLAIN_DEVICE")
    if not sent:
        raise RuntimeError("EXPLAIN_DEVICE is not set; start manimgx through explain.device.device_env")
    info = _engine.adapter_info()
    described = f"{info['name']} ({info['backend']})"
    on_cpu = info["device_type"] == "Cpu"
    if (sent == "cpu") != on_cpu:
        raise RuntimeError(f"Sent to {sent} but manimgx is on {described}")
    return described
