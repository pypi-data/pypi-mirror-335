"""Multipath device management.

This module provides functionality for managing multipath devices:
- Device discovery
- Path management
- Configuration management
- Service management

Device Mapper Multipath provides:
- I/O failover for redundancy
- I/O load balancing for performance
- Automatic path management
- Consistent device naming

Common use cases:
- High availability storage
- SAN connectivity
- iSCSI with multiple NICs
- FC with multiple HBAs
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Final, Literal

from sts.dm import DmDevice
from sts.utils.cmdline import run
from sts.utils.errors import DeviceError
from sts.utils.system import SystemManager

if TYPE_CHECKING:
    from collections.abc import Sequence

PACKAGE_NAME: Final[str] = 'device-mapper-multipath'


@dataclass
class MultipathDevice(DmDevice):
    """Multipath device representation.

    A multipath device combines multiple physical paths to the same storage
    into a single virtual device. This provides:
    - Automatic failover if paths fail
    - Load balancing across paths
    - Consistent device naming

    Args:
        name: Device name (optional, defaults to first available mpathX)
        path: Device path (optional, defaults to /dev/mapper/<name>)
        size: Device size in bytes (optional, discovered from device)
        dm_name: Device Mapper name (optional, discovered from device)
        model: Device model (optional)
        uuid: Device UUID (optional)
        wwid: Device WWID (optional, discovered from device)
        vendor: Device vendor (optional)
        paths: List of paths to device (HCTL and device node)

    Example:
        ```python
        print('kokot')
        device = MultipathDevice()  # Uses first available device
        device = MultipathDevice(name='mpatha')  # Uses specific device
        ```
    """

    # Optional parameters from parent classes
    name: str | None = None
    path: Path | str | None = None
    size: int | None = None
    dm_name: str | None = None
    model: str | None = None
    uuid: str | None = None

    # Optional parameters for this class
    wwid: str | None = None  # World Wide ID (unique identifier)
    vendor: str | None = None  # Device vendor
    paths: list[dict[str, Any]] = field(default_factory=list)  # Available paths

    # Configuration file paths
    MULTIPATH_CONF: ClassVar[Path] = Path('/etc/multipath.conf')
    MULTIPATH_BINDINGS: ClassVar[Path] = Path('/etc/multipath/bindings')

    def __post_init__(self) -> None:
        """Initialize multipath device.

        - Finds first available device if name not provided
        - Sets device path if not provided
        - Discovers device information and paths

        Raises:
            DeviceNotFoundError: If device does not exist
            DeviceError: If device cannot be accessed
        """
        # Get first available device if name not provided
        if not self.name:
            result = run('multipath -ll -v1')
            if result.succeeded and result.stdout:
                self.name = result.stdout.split()[0]

        # Set path based on name if not provided
        if not self.path and self.name:
            self.path = f'/dev/mapper/{self.name}'

        # Initialize parent class
        super().__post_init__()

        # Get device information if name provided
        if self.name:
            result = run(f'multipath -ll {self.name}')
            if result.succeeded:
                self._parse_device_info(result.stdout)

    def _parse_device_info(self, output: str) -> None:
        """Parse multipath -ll output for device information.

        Extracts key device information:
        - Device mapper name
        - World Wide ID (WWID)
        - Vendor and model
        - Path information

        Args:
            output: Output from multipath -ll command
        """
        # Parse first line for device info
        # Format: mpatha (360000000000000000e00000000000001) dm-0 VENDOR,PRODUCT
        if match := re.match(r'(\S+)\s+\((\S+)\)\s+(\S+)\s+([^,]+),(.+)', output.splitlines()[0]):
            if not self.dm_name:
                self.dm_name = match.group(3)
            if not self.wwid:
                self.wwid = match.group(2)
            if not self.vendor:
                self.vendor = match.group(4)
            if not self.model:
                self.model = match.group(5)

        # Parse paths section
        self._parse_paths(output)

    def _parse_paths(self, output: str) -> None:
        """Parse multipath -ll output for path information.

        Extracts information about each path:
        - SCSI HCTL (Host:Channel:Target:LUN)
        - Device node (e.g. sda)
        - Path state and priority

        Args:
            output: Output from multipath -ll command
        """
        current_path: dict[str, Any] = {}
        for line in output.splitlines():
            # Skip policy lines (separate path groups)
            if 'policy' in line:
                if current_path:
                    self.paths.append(current_path)
                    current_path = {}
                continue

            # Parse path line
            # Format: 1:0:0:0 sda 8:0   active ready running
            if match := re.match(r'\s*(\d+:\d+:\d+:\d+)\s+(\w+)\s+', line):
                if current_path:
                    self.paths.append(current_path)
                current_path = {
                    'hctl': match.group(1),  # SCSI address
                    'dev': match.group(2),  # Device node
                }

        # Add last path if any
        if current_path:
            self.paths.append(current_path)

    def suspend(self) -> bool:
        """Suspend device.

        Temporarily disables the multipath device:
        - Stops using device for I/O
        - Keeps paths configured
        - Device can be resumed later

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.suspend()
            True
            ```
        """
        if not self.name:
            logging.error('Device name not available')
            return False

        result = run(f'multipath -f {self.name}')
        if result.failed:
            logging.error('Failed to suspend device')
            return False
        return True

    def resume(self) -> bool:
        """Resume device.

        Re-enables a suspended multipath device:
        - Rescans paths
        - Restores device operation
        - Resumes I/O handling

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.resume()
            True
            ```
        """
        if not self.name:
            logging.error('Device name not available')
            return False

        result = run(f'multipath -a {self.name}')
        if result.failed:
            logging.error('Failed to resume device')
            return False
        return True

    def remove(self) -> bool:
        """Remove device.

        Completely removes the multipath device:
        - Flushes I/O
        - Removes device mapper table
        - Clears path information

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.remove()
            True
            ```
        """
        if not self.name:
            logging.error('Device name not available')
            return False

        result = run(f'multipath -f {self.name}')
        if result.failed:
            logging.error('Failed to remove device')
            return False
        return True

    @classmethod
    def get_all(cls) -> Sequence[DmDevice]:
        """Get list of all multipath devices.

        Lists all configured multipath devices:
        - Includes active and inactive devices
        - Provides basic device information
        - Does not include detailed path status

        Returns:
            List of MultipathDevice instances

        Example:
            ```python
            MultipathDevice.get_all()
            [MultipathDevice(name='mpatha', ...), MultipathDevice(name='mpathb', ...)]
            ```
        """
        devices = []
        result = run('multipath -ll -v2')
        if result.failed:
            logging.warning('No multipath devices found')
            return []

        # Parse line like: mpatha (360000000000000000e00000000000001) dm-0 VENDOR,PRODUCT
        # or 360a98000324669436c2b45666c567863 dm-6 VENDOR,PRODUCT
        patterns = [r'(\S+)\s+(\S+)\s+([^,]+),(.+)', r'(\S+)\s+\((\S+)\)\s+(\S+)\s+([^,]+),(.+)']
        for line in result.stdout.splitlines():
            try:
                match = next((m for p in patterns if (m := re.match(p, line))), None)
                if match:
                    groups = match.groups()
                    wwid, dm_name, vendor, product = groups[:4]
                    name = groups[0] if len(groups) == 5 else None
                    devices.append(cls(name=name, dm_name=dm_name, wwid=wwid, vendor=vendor, model=product))
            except (ValueError, DeviceError):  # noqa: PERF203
                logging.exception(f'Failed to parse device info for line: {line}')

        return devices

    @classmethod
    def get_by_wwid(cls, wwid: str) -> MultipathDevice | None:
        """Get multipath device by WWID.

        The World Wide ID uniquely identifies a storage device:
        - Consistent across reboots
        - Same for all paths to device
        - Vendor-specific format

        Args:
            wwid: Device WWID

        Returns:
            MultipathDevice instance or None if not found

        Example:
            ```python
            MultipathDevice.get_by_wwid('360000000000000000e00000000000001')
            MultipathDevice(name='mpatha', ...)
            ```
        """
        if not wwid:
            msg = 'WWID required'
            raise ValueError(msg)

        for device in cls.get_all():
            if isinstance(device, MultipathDevice) and device.wwid == wwid:
                return device

        return None


class MultipathService:
    """Multipath service management.

    Manages the multipathd service which:
    - Monitors path status
    - Handles path failures
    - Manages device creation
    - Applies configuration

    Example:
        ```python
        service = MultipathService()
        service.start()
        True
        ```
    """

    def __init__(self) -> None:
        """Initialize multipath service."""
        self.config_path = MultipathDevice.MULTIPATH_CONF
        # Ensure package is installed
        system = SystemManager()
        if not system.package_manager.install(PACKAGE_NAME):
            logging.critical(f'Could not install {PACKAGE_NAME}')

    def start(self) -> bool:
        """Start multipath service.

        Starts the multipathd daemon:
        - Creates default config if needed
        - Starts systemd service
        - Begins path monitoring

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            service.start()
            True
            ```
        """
        # Create default config if needed
        if not self.config_path.exists():
            result = run('mpathconf --enable')
            if result.failed:
                logging.error('Failed to create default config')
                return False

        result = run('systemctl start multipathd')
        if result.failed:
            logging.error('Failed to start multipathd')
            return False

        return True

    def stop(self) -> bool:
        """Stop multipath service.

        Stops the multipathd daemon:
        - Stops path monitoring
        - Keeps devices configured
        - Maintains configuration

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            service.stop()
            True
            ```
        """
        result = run('systemctl stop multipathd')
        if result.failed:
            logging.error('Failed to stop multipathd')
            return False

        return True

    def reload(self) -> bool:
        """Reload multipath configuration.

        Reloads configuration without restart:
        - Applies config changes
        - Keeps devices active
        - Updates path settings

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            service.reload()
            True
            ```
        """
        result = run('systemctl reload multipathd')
        if result.failed:
            logging.error('Failed to reload multipathd')
            return False

        return True

    def is_running(self) -> bool:
        """Check if multipath service is running.

        Returns:
            True if running, False otherwise

        Example:
            ```python
            service.is_running()
            True
            ```
        """
        result = run('systemctl is-active multipathd')
        return result.succeeded

    def configure(
        self,
        find_multipaths: Literal['yes', 'no', 'strict', 'greedy', 'smart'] | None = None,
    ) -> bool:
        """Configure multipath service.

        Sets up multipath configuration:
        - find_multipaths modes:
          - yes: Create multipath devices for likely candidates
          - no: Only create explicitly configured devices
          - strict: Only create devices with multiple paths
          - greedy: Create devices for all SCSI devices
          - smart: Create devices based on WWID patterns

        Args:
            find_multipaths: How to detect multipath devices

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            service.configure(find_multipaths='yes')
            True
            ```
        """
        cmd = ['mpathconf', '--enable']
        if find_multipaths:
            cmd.extend(['--find_multipaths', find_multipaths])

        result = run(' '.join(cmd))
        if result.failed:
            logging.error('Failed to configure multipathd')
            return False

        return True

    def get_paths(self, device: str) -> list[dict[str, Any]]:
        """Get paths for device.

        Lists all paths for a device with status:
        - Device node (e.g. sda)
        - DM state (active/passive)
        - Path state (ready/failed)
        - Online state (running/offline)

        Args:
            device: Device name or WWID

        Returns:
            List of path dictionaries

        Example:
            ```python
            service.get_paths('mpatha')
            [{'hctl': '1:0:0:0', 'dev': 'sda', 'state': 'active'}, ...]
            ```
        """
        result = run('multipathd show paths format "%d %t %T"')
        if result.failed:
            return []

        paths = []
        for line in result.stdout.splitlines():
            if device not in line:
                continue

            # Parse line like: sda active ready running
            parts = line.split()
            if len(parts) < 4:
                continue

            paths.append(
                {
                    'dev': parts[0],  # Device node
                    'dm_state': parts[1],  # Device mapper state
                    'path_state': parts[2],  # Path health
                    'online_state': parts[3],  # Connection status
                }
            )

        return paths

    def flush(self) -> bool:
        """Flush all unused multipath devices.

        Removes unused multipath devices:
        - Clears device mapper tables
        - Removes path groups
        - Keeps configuration intact

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            service.flush()
            True
            ```
        """
        result = run('multipath -F')
        if result.failed:
            logging.error('Failed to flush devices')
            return False

        return True
