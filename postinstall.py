#!/usr/bin/env python
import subprocess
import sys

def install_playwright_browsers():
    """Install Playwright browsers during deployment"""
    try:
        print("Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("Playwright browsers installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Playwright browsers: {e}")
        sys.exit(1)

def main():
    install_playwright_browsers()

if __name__ == "__main__":
    main()