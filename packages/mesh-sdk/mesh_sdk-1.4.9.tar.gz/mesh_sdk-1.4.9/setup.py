from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys
import webbrowser

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        try:
            # Only run auth flow if not in CI/CD
            if not os.environ.get('CI'):
                print("\nRunning post-install authentication flow...")
                from mesh.auth import authenticate
                authenticate()
        except Exception as e:
            print(f"\nNote: Post-install authentication failed: {e}")
            print("You can authenticate later by running 'mesh-auth' from the command line")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mesh-sdk",
    version="1.4.9",
    author="Mesh Team",
    author_email="support@meshsdk.io",
    description="Official Python SDK for the Mesh API - Secure key management and AI model access",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meshsdk/mesh-python",
    project_urls={
        "Documentation": "https://docs.meshsdk.io",
        "Source": "https://github.com/meshsdk/mesh-python",
        "Issues": "https://github.com/meshsdk/mesh-python/issues",
    },
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    install_requires=[
        "requests>=2.31.0",
        "keyring>=24.3.0",
        "cryptography>=42.0.0",
        "pyjwt>=2.8.0",
        "urllib3>=2.0.0",
        "certifi>=2024.2.0",
        "pillow>=10.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=24.0.0",
            "isort>=5.13.0",
            "mypy>=1.8.0",
            "types-requests>=2.31.0",
            "types-urllib3>=1.26.25"
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=2.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "mesh-auth=mesh.auth_cli:main",
        ],
    },
    cmdclass={
        "install": PostInstallCommand,
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    keywords="mesh, api, sdk, security, key management, zero knowledge proofs, ai, openai, anthropic",
) 