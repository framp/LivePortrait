import os
import glob
import subprocess
import sys
import warnings
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from setuptools.command.develop import develop

class BuildMSDAMixin:
    """Mixin class for building MultiScaleDeformableAttention"""

    def build_msda(self):
        """Build MultiScaleDeformableAttention CUDA extension"""
        msda_path = os.path.join(
            os.path.dirname(__file__),
            'src', 'utils', 'dependencies', 'XPose', 'models', 'UniPose', 'ops'
        )

        if not os.path.exists(msda_path):
            warnings.warn("MultiScaleDeformableAttention source not found. Skipping CUDA extension build.")
            return False

        try:
            # Check if CUDA is available
            import torch
            if not torch.cuda.is_available():
                warnings.warn("CUDA not available. MultiScaleDeformableAttention will use PyTorch fallback.")
                return False

            print("Building MultiScaleDeformableAttention CUDA extension...")

            # Change to the ops directory and run setup.py
            original_cwd = os.getcwd()
            try:
                os.chdir(msda_path)
                result = subprocess.run([
                    sys.executable, 'setup.py', 'build_ext', '--inplace'
                ], capture_output=True, text=True)

                if result.returncode != 0:
                    warnings.warn(f"Failed to build MultiScaleDeformableAttention: {result.stderr}")
                    warnings.warn("Will use PyTorch fallback instead.")
                    return False
                else:
                    print("MultiScaleDeformableAttention built successfully!")
                    return True

            finally:
                os.chdir(original_cwd)

        except Exception as e:
            warnings.warn(f"Error building MultiScaleDeformableAttention: {e}")
            warnings.warn("Will use PyTorch fallback instead.")
            return False

class BuildExtCommand(build_ext, BuildMSDAMixin):
    """Custom build_ext command that builds MultiScaleDeformableAttention"""

    def run(self):
        # First run the normal build_ext
        super().run()

        # Then build the MultiScaleDeformableAttention extension
        self.build_msda()

class InstallCommand(install, BuildMSDAMixin):
    """Custom install command that ensures CUDA extension is built"""

    def run(self):
        super().run()
        # Build MSDA after installation
        self.build_msda()

class DevelopCommand(develop, BuildMSDAMixin):
    """Custom develop command that builds CUDA extension in development mode"""

    def run(self):
        super().run()
        # Build MSDA after development installation
        self.build_msda()

if __name__ == "__main__":
    setup(
        cmdclass={
            'build_ext': BuildExtCommand,
            'install': InstallCommand,
            'develop': DevelopCommand,
        }
    )
