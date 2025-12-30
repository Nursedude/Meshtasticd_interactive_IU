#!/usr/bin/env python3
"""
Comprehensive Test Suite for Meshtasticd Interactive Installer
Tests all major functionality before deployment
"""

import os
import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;36m'
    BOLD = '\033[1m'
    END = '\033[0m'


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.repo_root = Path(__file__).parent.parent

    def test(self, name, func):
        """Run a test and track results"""
        try:
            print(f"\n{Colors.BLUE}Testing:{Colors.END} {name}")
            func()
            print(f"{Colors.GREEN}✓ PASS{Colors.END}")
            self.passed += 1
            self.tests.append((name, "PASS"))
            return True
        except AssertionError as e:
            print(f"{Colors.RED}✗ FAIL: {e}{Colors.END}")
            self.failed += 1
            self.tests.append((name, f"FAIL: {e}"))
            return False
        except Exception as e:
            print(f"{Colors.RED}✗ ERROR: {e}{Colors.END}")
            self.failed += 1
            self.tests.append((name, f"ERROR: {e}"))
            return False

    def report(self):
        """Print test report"""
        total = self.passed + self.failed
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Test Results{Colors.END}")
        print(f"{'='*60}")
        print(f"Total: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        if total > 0:
            print(f"Success Rate: {(self.passed/total*100):.1f}%")
        print(f"{'='*60}\n")

        return self.failed == 0


def test_imports():
    """Test that all required modules can be imported"""
    import click
    import rich
    import yaml
    import requests
    import psutil
    import distro
    import dotenv
    import meshtastic
    assert True


def test_emoji_system():
    """Test emoji helper functionality"""
    from utils.emoji import EmojiHelper

    em = EmojiHelper()

    # Test fallback mode
    em.disable()
    assert em.get('🟢') == '[*]', "Emoji fallback should return ASCII"

    # Test enabled mode
    em.enable()
    assert em.get('🟢') == '🟢', "Emoji should return emoji when enabled"

    # Test custom fallback
    em.disable()
    assert em.get('🟢', '[OK]') == '[OK]', "Custom fallback should work"


def test_logger_setup():
    """Test logger initialization"""
    from utils.logger import setup_logger, get_logger

    result_logger = setup_logger(debug=True)
    assert result_logger is not None, "Logger should be initialized"

    # Also test get_logger function
    logger = get_logger()
    assert logger is not None, "get_logger() should return logger"


def test_config_module():
    """Test configuration loading"""
    from utils.config import (
        MESHTASTICD_CONFIG_PATH,
        LOG_LEVEL,
        DEBUG_MODE,
        ENABLE_EMOJI
    )

    assert MESHTASTICD_CONFIG_PATH is not None
    assert LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    assert isinstance(DEBUG_MODE, bool)
    assert isinstance(ENABLE_EMOJI, bool)


def test_system_utils():
    """Test system utility functions"""
    from utils.system import get_system_info, get_os_type

    info = get_system_info()
    assert 'os' in info
    assert 'arch' in info
    assert 'bits' in info

    os_type = get_os_type()
    assert os_type in ['armhf', 'arm64', 'x86_64', 'unknown']


def test_hardware_config():
    """Test hardware configuration loading"""
    from config.hardware import get_available_hats, detect_usb_devices

    hats = get_available_hats()
    assert isinstance(hats, dict), "Should return dict of HATs"
    assert len(hats) > 0, "Should have some HAT definitions"

    # USB detection should not crash (may return empty list in test env)
    devices = detect_usb_devices()
    assert isinstance(devices, list), "Should return list of devices"


def test_lora_regions():
    """Test LoRa region configurations"""
    from config.lora import REGIONS, MODEM_PRESETS

    assert 'US' in REGIONS, "Should have US region"
    assert 'EU_868' in REGIONS, "Should have EU_868 region"

    assert 'LONG_FAST' in MODEM_PRESETS, "Should have LONG_FAST preset"
    assert 'MEDIUM_FAST' in MODEM_PRESETS, "Should have MEDIUM_FAST preset"


def test_channel_presets():
    """Test channel preset configurations"""
    from config.channel_presets import get_all_presets, get_preset

    presets = get_all_presets()
    assert isinstance(presets, dict), "Should return dict of presets"
    assert len(presets) > 0, "Should have channel presets"

    # Test getting a specific preset
    default = get_preset('default')
    assert default is not None, "Should have default preset"


def test_module_configs():
    """Test module configuration options"""
    from config.modules import MODULES

    assert isinstance(MODULES, dict), "MODULES should be a dict"
    assert 'mqtt' in MODULES, "Should have MQTT module"
    assert 'serial' in MODULES, "Should have Serial module"


def test_installer_class():
    """Test MeshtasticdInstaller initialization"""
    from installer.meshtasticd import MeshtasticdInstaller

    installer = MeshtasticdInstaller()
    assert installer is not None
    assert hasattr(installer, 'install')
    assert hasattr(installer, 'update')
    assert hasattr(installer, 'check_prerequisites')


def test_cli_commands():
    """Test CLI command structure"""
    result = subprocess.run(
        ['venv/bin/python', 'src/main.py', '--help'],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )

    assert result.returncode == 0, "Help command should succeed"
    assert '--install' in result.stdout, "Should have install option"
    assert '--configure' in result.stdout, "Should have configure option"
    assert '--dashboard' in result.stdout, "Should have dashboard option"


def test_version_command():
    """Test version command"""
    result = subprocess.run(
        ['venv/bin/python', 'src/main.py', '--version'],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )

    assert result.returncode == 0, "Version command should succeed"
    assert 'v2.0' in result.stdout, "Should show version number"


def test_templates_exist():
    """Test that configuration templates exist"""
    templates_dir = Path(__file__).parent.parent / 'templates'

    assert templates_dir.exists(), "Templates directory should exist"

    available_d = templates_dir / 'available.d'
    assert available_d.exists(), "available.d directory should exist"

    # Check for some expected templates
    templates = list(available_d.glob('*.yaml'))
    assert len(templates) > 0, "Should have template files"


def test_scripts_exist():
    """Test that installation scripts exist"""
    scripts_dir = Path(__file__).parent.parent / 'scripts'

    assert scripts_dir.exists(), "Scripts directory should exist"

    # Check for expected scripts
    assert (scripts_dir / 'install_armhf.sh').exists(), "armhf script should exist"
    assert (scripts_dir / 'install_arm64.sh').exists(), "arm64 script should exist"
    assert (scripts_dir / 'setup_permissions.sh').exists(), "permissions script should exist"


def test_env_example():
    """Test that .env.example is valid"""
    env_example = Path(__file__).parent.parent / '.env.example'

    assert env_example.exists(), ".env.example should exist"

    content = env_example.read_text()
    assert 'ENABLE_EMOJI' in content, "Should have ENABLE_EMOJI setting"
    assert 'DEBUG_MODE' in content, "Should have DEBUG_MODE setting"
    assert 'LOG_LEVEL' in content, "Should have LOG_LEVEL setting"


def test_readme_exists():
    """Test that documentation exists"""
    readme = Path(__file__).parent.parent / 'README.md'
    assert readme.exists(), "README.md should exist"

    quick_start = Path(__file__).parent.parent / 'QUICK_START.md'
    assert quick_start.exists(), "QUICK_START.md should exist"


def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   Meshtasticd Installer - Test Suite                     ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")

    runner = TestRunner()

    # Core functionality tests
    print(f"\n{Colors.BOLD}Core Functionality Tests{Colors.END}")
    runner.test("Import all dependencies", test_imports)
    runner.test("Logger setup", test_logger_setup)
    runner.test("Configuration module", test_config_module)
    runner.test("System utilities", test_system_utils)

    # UI/Display tests
    print(f"\n{Colors.BOLD}UI & Display Tests{Colors.END}")
    runner.test("Emoji system", test_emoji_system)

    # Configuration tests
    print(f"\n{Colors.BOLD}Configuration Tests{Colors.END}")
    runner.test("Hardware configurations", test_hardware_config)
    runner.test("LoRa regions and presets", test_lora_regions)
    runner.test("Channel presets", test_channel_presets)
    runner.test("Module configurations", test_module_configs)

    # Installer tests
    print(f"\n{Colors.BOLD}Installer Tests{Colors.END}")
    runner.test("Installer class", test_installer_class)

    # CLI tests
    print(f"\n{Colors.BOLD}CLI Tests{Colors.END}")
    runner.test("CLI commands", test_cli_commands)
    runner.test("Version command", test_version_command)

    # File structure tests
    print(f"\n{Colors.BOLD}File Structure Tests{Colors.END}")
    runner.test("Configuration templates", test_templates_exist)
    runner.test("Installation scripts", test_scripts_exist)
    runner.test("Environment example file", test_env_example)
    runner.test("Documentation files", test_readme_exists)

    # Print report
    success = runner.report()

    if success:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All tests passed!{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some tests failed!{Colors.END}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
