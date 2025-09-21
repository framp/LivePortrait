#!/usr/bin/env python
"""
Script to build MultiScaleDeformableAttention CUDA extension
This can be run manually or called during package installation
"""

import os
import subprocess
import sys
import warnings

def build_msda():
    """Build MultiScaleDeformableAttention CUDA extension"""
    # Get the path to the ops directory
    script_dir = os.path.dirname(__file__)
    msda_path = os.path.join(
        script_dir,
        'src', 'utils', 'dependencies', 'XPose', 'models', 'UniPose', 'ops'
    )

    if not os.path.exists(msda_path):
        warnings.warn("MultiScaleDeformableAttention source not found. Skipping CUDA extension build.")
        return False

    try:
        # Check if CUDA is available
        import torch
        if not torch.cuda.is_available():
            print("CUDA not available. MultiScaleDeformableAttention will use PyTorch fallback.")
            return False

        print("Building MultiScaleDeformableAttention CUDA extension...")

        # Change to the ops directory and run setup.py
        original_cwd = os.getcwd()
        try:
            os.chdir(msda_path)
            result = subprocess.run([
                sys.executable, 'setup.py', 'build_ext', '--inplace'
            ], capture_output=False, text=True)

            if result.returncode != 0:
                print(f"Failed to build MultiScaleDeformableAttention (exit code: {result.returncode})")
                print("Will use PyTorch fallback instead.")
                return False
            else:
                print("MultiScaleDeformableAttention built successfully!")
                return True

        finally:
            os.chdir(original_cwd)

    except Exception as e:
        print(f"Error building MultiScaleDeformableAttention: {e}")
        print("Will use PyTorch fallback instead.")
        return False

if __name__ == "__main__":
    success = build_msda()
    sys.exit(0 if success else 1)
