# Copyright 2024 Garena Online Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import glob
import os
import sys


def find_cuda_library():
    """Finds libcudart.so in Python's site-packages or standard CUDA paths."""
    # Search in Python site-packages (virtualenv or conda)
    site_packages_paths = [
        p for p in sys.path if "site-packages" in p or "dist-packages" in p
    ]

    for path in site_packages_paths:
        # Look for common CUDA library locations inside site-packages
        cuda_libs = glob.glob(
            os.path.join(path, "nvidia/cuda_runtime/lib/libcudart.so*")
        )
        if cuda_libs:
            return os.path.dirname(cuda_libs[0])

    # Fallback: Standard system CUDA locations
    possible_paths = [
        "/usr/local/cuda/lib64",
        "/usr/local/cuda-11.0/lib64",
        "/usr/lib/x86_64-linux-gnu/",
    ]

    for cuda_path in glob.glob("/usr/local/cuda-*"):
        lib_path = os.path.join(cuda_path, "lib64")
        if os.path.exists(os.path.join(lib_path, "libcudart.so")):
            possible_paths.append(lib_path)

    for path in possible_paths:
        if os.path.exists(os.path.join(path, "libcudart.so")):
            return path

    return None


# Find CUDA library path & export to LD_LIBRARY_PATH to be found by dependencies.
cuda_lib_path = find_cuda_library()
if cuda_lib_path:
    os.environ["LD_LIBRARY_PATH"] = (
        cuda_lib_path + ":" + os.environ.get("LD_LIBRARY_PATH", "")
    )
    sys.stderr.write(f"Set LD_LIBRARY_PATH={os.environ['LD_LIBRARY_PATH']}\n")
