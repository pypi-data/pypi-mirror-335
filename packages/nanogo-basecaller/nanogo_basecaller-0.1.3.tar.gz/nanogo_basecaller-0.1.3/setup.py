import setuptools
import os
import sys
import hashlib
import tarfile
import urllib.request
import shutil
import tempfile
import re
import json
from setuptools.command.install import install


# Fallback version info if we can't fetch the latest
FALLBACK_DORADO_URL = (
    "https://cdn.oxfordnanoportal.com/software/analysis/dorado-0.9.1-linux-x64.tar.gz"
)
FALLBACK_DORADO_SHA256 = (
    "acc0d28310e3df44bd88efd67fa949eb2d43b183c335c0964d7fe109a0ad56c1"
)
DORADO_BIN = os.path.join(sys.prefix, "bin", "dorado")


def get_latest_dorado_version():
    """
    Check ONT's CDN for the latest version of Dorado.
    Returns a tuple of (version, url, sha256) or None if unable to determine.
    """
    try:
        # This URL is a placeholder - ONT might have an API or index page we can parse
        index_url = "https://cdn.oxfordnanoportal.com/software/analysis/"

        with urllib.request.urlopen(index_url) as response:
            html = response.read().decode("utf-8")

            # Look for dorado release tarballs in the HTML
            # This regex pattern looks for Linux x64 tarballs
            pattern = r'href="(dorado-(\d+\.\d+\.\d+)-linux-x64\.tar\.gz)"'
            matches = re.findall(pattern, html)

            if not matches:
                print("No Dorado releases found, falling back to default version.")
                return None

            # Sort by version number to find the latest
            latest = sorted(
                matches, key=lambda x: [int(n) for n in x[1].split(".")], reverse=True
            )[0]
            latest_filename = latest[0]
            latest_version = latest[1]

            # Construct the full URL
            latest_url = f"{index_url}{latest_filename}"

            # Now we need to get the SHA256 hash
            # ONT might provide this in a separate file, or we might need to calculate it
            # For now, we'll try to see if there's a .sha256 file
            try:
                hash_url = f"{latest_url}.sha256"
                with urllib.request.urlopen(hash_url) as hash_response:
                    sha256 = hash_response.read().decode("utf-8").strip().split()[0]
                    return (latest_version, latest_url, sha256)
            except urllib.error.URLError:
                # If we can't get the hash file, we'll need to fetch and hash the tarball
                print(
                    f"SHA256 file not found for {latest_filename}. Will verify after download."
                )
                return (latest_version, latest_url, None)

    except Exception as e:
        print(f"Error checking for latest Dorado version: {e}")
        print("Falling back to default version.")
        return None


def is_dorado_installed():
    """Check if Dorado is already installed."""
    # Check if the main executable exists
    if not os.path.exists(DORADO_BIN):
        return False

    # Optionally check if it's executable
    if not os.access(DORADO_BIN, os.X_OK):
        return False

    # Optionally check if libraries are installed
    lib_dir = os.path.join(sys.prefix, "lib")
    dorado_libs = [file for file in os.listdir(lib_dir) if file.startswith("libdorado")]
    if len(dorado_libs) == 0:
        return False

    return True


def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def install_dorado():
    """Install Dorado if not already installed, trying to use the latest version."""
    if is_dorado_installed():
        print("Dorado already installed. Skipping installation.")
        return

    # Try to get latest version info
    latest_info = get_latest_dorado_version()

    if latest_info:
        version, url, sha256 = latest_info
        print(f"Found latest Dorado version: {version}")
        expected_dir_name = f"dorado-{version}-linux-x64"
    else:
        # Fall back to the hardcoded version
        version = "0.9.1"  # Extracted from the URL
        url = FALLBACK_DORADO_URL
        sha256 = FALLBACK_DORADO_SHA256
        expected_dir_name = "dorado-0.9.1-linux-x64"
        print(f"Using fallback Dorado version: {version}")

    # Create a temporary directory for download and extraction
    tmp_dir = tempfile.mkdtemp()
    tarball_path = os.path.join(tmp_dir, "dorado.tar.gz")

    print(f"Downloading Dorado {version}...")
    urllib.request.urlretrieve(url, tarball_path)

    print("Verifying download...")
    if sha256:
        # Verify against provided hash
        calculated_hash = calculate_sha256(tarball_path)
        if calculated_hash != sha256:
            raise ValueError(
                f"SHA256 hash verification failed for Dorado download.\n"
                f"Expected: {sha256}\n"
                f"Got: {calculated_hash}"
            )
        print("✓ SHA256 verified.")
    else:
        # If we don't have a hash to verify against, just log the hash we calculated
        calculated_hash = calculate_sha256(tarball_path)
        print(f"Downloaded file SHA256: {calculated_hash}")
        print("⚠️ No SHA256 hash available to verify against.")

    print("Extracting Dorado...")
    with tarfile.open(tarball_path, "r:gz") as tar:
        tar.extractall(path=tmp_dir)

    # Find the extracted directory
    extracted_contents = os.listdir(tmp_dir)
    extracted_dirs = [
        d
        for d in extracted_contents
        if os.path.isdir(os.path.join(tmp_dir, d)) and d.startswith("dorado-")
    ]

    if not extracted_dirs:
        raise FileNotFoundError(
            f"Could not find Dorado directory in extracted contents: {extracted_contents}"
        )

    # Use the first directory that matches the pattern
    extracted_dir = os.path.join(tmp_dir, extracted_dirs[0])

    extracted_bin = os.path.join(extracted_dir, "bin")
    extracted_lib = os.path.join(extracted_dir, "lib")

    # Determine the target directories
    bin_target = os.path.join(sys.prefix, "bin")
    lib_target = os.path.join(sys.prefix, "lib")

    print(f"Moving files from {extracted_bin} to {bin_target}...")
    # Move all files from the extracted bin folder
    for filename in os.listdir(extracted_bin):
        src = os.path.join(extracted_bin, filename)
        dst = os.path.join(bin_target, filename)
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        shutil.move(src, dst)
        os.chmod(dst, 0o755)

    print(f"Moving files from {extracted_lib} to {lib_target}...")
    # Move all files from the extracted lib folder
    for filename in os.listdir(extracted_lib):
        src = os.path.join(extracted_lib, filename)
        dst = os.path.join(lib_target, filename)
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        shutil.move(src, dst)

    print(f"✓ Dorado {version} installed successfully.")

    # Cleanup the temporary directory
    shutil.rmtree(tmp_dir)


class CustomInstallCommand(install):
    """Customized setuptools install command to download and install Dorado."""

    def run(self):
        # Run the standard installation
        install.run(self)
        # Then perform the Dorado installation
        install_dorado()


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nanogo-basecaller",
    version="0.1.3",
    author="Gurasis Osahan",
    author_email="gurasis.osahan@phac-aspc.gc.ca",
    description="A bioinformatics pipeline for basecalling ONT NGS Data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phac-nml/nanogo-basecaller",
    cmdclass={"install": CustomInstallCommand},
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires="<=3.11",
    install_requires=[
        "about-time>=4.2.1",
        "alive-progress>=3.2.0",
        "anyio>=4.9.0",
        "bio>=1.7.1",
        "biopython>=1.85",
        "biothings-client>=0.4.1",
        "build>=1.2.2.post1",
        "certifi>=2025.1.31",
        "charset-normalizer>=3.4.1",
        "contourpy>=1.3.1",
        "cycler>=0.12.1",
        "cython>=3.0.12",
        "et-xmlfile>=2.0.0",
        "exceptiongroup>=1.2.2",
        "fonttools>=4.56.0",
        "gprofiler-official>=1.0.0",
        "gputil>=1.4.0",
        "grapheme>=0.6.0",
        "h11>=0.14.0",
        "h5py>=3.10.0",
        "httpcore>=1.0.7",
        "httpx>=0.28.1",
        "idna>=3.10",
        "iso8601>=2.1.0",
        "kiwisolver>=1.4.8",
        "lib-pod5>=0.3.10",
        "matplotlib>=3.10.1",
        "more-itertools>=10.6.0",
        "mygene>=3.2.2",
        "narwhals>=1.31.0",
        "numpy<2.0.0, >=1.24.3",
        "openpyxl>=3.1.5",
        "packaging>=24.2",
        "pandas>=2.2.3",
        "pillow>=11.1.0",
        "platformdirs>=4.3.6",
        "plotly>=6.0.1",
        "pod5==0.3.10",
        "poetry-core>=2.1.1",
        "polars>=0.20.31",
        "pooch>=1.8.2",
        "psutil>=7.0.0",
        "pyarrow>=14.0.2",
        "pyparsing>=3.2.1",
        "pyproject-hooks>=1.2.0",
        "python-dateutil>=2.9.0.post0",
        "pytz>=2025.1",
        "requests>=2.32.3",
        "scipy>=1.15.2",
        "six>=1.17.0",
        "sniffio>=1.3.1",
        "tomli>=2.2.1",
        "tqdm>=4.67.1",
        "typing-extensions>=4.12.2",
        "tzdata>=2025.1",
        "urllib3>=2.3.0",
        "vbz-h5py-plugin>=1.0.1",
        "wheel>=0.45.1",
    ],
    entry_points={"console_scripts": ["nanogo=nanogo_basecaller.cli:main"]},
    keywords="nanopore sequencing ONT bioinformatics dorado basecalling NGS pipeline primer-trimming",
    license="GPL-3.0-or-later",
    project_urls={
        "Source": "https://github.com/phac-nml/nanogo-basecaller",
        "Tracker": "https://github.com/phac-nml/nanogo-basecaller/-/issues",
        "Documentation": "https://github.com/phac-nml/nanogo-basecaller/wiki",
        "Publication": "https://github.com/phac-nml/nanogo-basecaller#citation",
        "Contact": "https://github.com/phac-nml/nanogo-basecaller#contact",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
        "Environment :: GPU :: NVIDIA CUDA",
        "Environment :: Console",
        "Framework :: Pytest",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
