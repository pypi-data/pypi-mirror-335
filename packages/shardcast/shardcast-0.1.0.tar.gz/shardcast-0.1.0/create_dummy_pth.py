#!/usr/bin/env python3
"""
Script to create a dummy PyTorch .pth file of specified size.
Default size is 1.5GB, with configurable output path and filename.

1. Uses PyTorch to create a file with random tensor data
2. Takes 3 CLI parameters:
- --size (or -s): size in GB (default: 1.5GB)
- --path (or -p): output directory (default: current directory)
- --name (or -n): output filename (default: dummy_model.pth)
3. Generates a SHA-256 checksum of the created file
4. Displays file info after creation

You can run it with:
./create_dummy_pth.py

Or with custom options:
python3 create_dummy_pth.py --size 2.0 --path /tmp --name large_dummy_model.pth
"""

import os
import argparse
import hashlib
import torch
import numpy as np
from pathlib import Path


def create_dummy_file(size_gb, output_path, output_name):
    """Create a dummy PyTorch .pth file of specified size.
    
    Args:
        size_gb (float): Size of the file in GB
        output_path (str): Directory to save the file
        output_name (str): Name of the output file
    
    Returns:
        str: SHA-256 checksum of created file
    """
    os.makedirs(output_path, exist_ok=True)
    
    full_path = os.path.join(output_path, output_name)
    
    # calc size in bytes
    size_bytes = int(size_gb * 1024 * 1024 * 1024)
    
    print(f"Creating dummy file: {full_path} ({size_gb} GB)")
    print("This may take some time depending on the file size...")
    
    # calculate how many tensors and what size to achieve target file size
    # a rough estimate - final file size might vary slightly
    tensor_size = int(np.sqrt(size_bytes / 8))  # 8 bytes per float64
    
    # Create a dummy model with random tensors
    dummy_model = {
        f"layer_{i}": torch.rand(tensor_size, tensor_size, dtype=torch.float64)
        for i in range(3)  # Creating multiple tensors for a more realistic model structure
    }
    
    # Save the model
    torch.save(dummy_model, full_path)
    
    actual_size = os.path.getsize(full_path)
    actual_size_gb = actual_size / (1024**3)
    
    sha256 = hashlib.sha256()
    with open(full_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    checksum = sha256.hexdigest()
    
    print("File created successfully!")
    print(f"Path: {full_path}")
    print(f"Size: {actual_size_gb:.2f} GB ({format_size(actual_size)})")
    print(f"SHA-256: {checksum}")
    
    return checksum


def format_size(size_bytes):
    """Format file size in a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024 or unit == 'GB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024


def main():
    parser = argparse.ArgumentParser(description="Create a dummy PyTorch .pth file")
    parser.add_argument("-s", "--size", type=float, default=1.5,
                        help="Size of the file in GB (default: 1.5)")
    parser.add_argument("-p", "--path", type=str, default=".",
                        help="Output directory path (default: current directory)")
    parser.add_argument("-n", "--name", type=str, default="dummy_model.pth",
                        help="Output filename (default: dummy_model.pth)")
    
    args = parser.parse_args()
    
    create_dummy_file(args.size, args.path, args.name)


if __name__ == "__main__":
    main()