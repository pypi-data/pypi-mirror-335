"""SCSI device management.

This module provides functionality for managing SCSI devices:
- Device discovery
- Device information
- Device operations

SCSI (Small Computer System Interface) is a standard for:
- Storage device communication
- Device addressing and identification
- Command and data transfer
- Error handling and recovery

Common SCSI devices include:
- Hard drives (HDDs)
- Solid State Drives (SSDs)
- Tape drives
- CD/DVD/Blu-ray drives
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

import contextlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from sts.base import StorageDevice
from sts.utils.cmdline import run
from sts.utils.packages import ensure_installed


@dataclass
class ScsiDevice(StorageDevice):
    """SCSI device representation.

    A SCSI device is identified by:
    - SCSI ID (H:C:T:L format)
      - H: Host adapter number
      - C: Channel/Bus number
      - T: Target ID
      - L: Logical Unit Number (LUN)
    - Device node (e.g. /dev/sda)
    - Vendor and model information

    Args:
        name: Device name (optional, e.g. 'sda')
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        scsi_id: SCSI ID (optional, discovered from device)

    Example:
        ```python
        device = ScsiDevice(name='sda')  # Discovers other values
        device = ScsiDevice(scsi_id='0:0:0:0')  # Discovers device from SCSI ID
        ```
    """

    # Optional parameters from parent classes
    name: str | None = None
    path: Path | str | None = None
    size: int | None = None
    model: str | None = None

    # Optional parameters for this class
    scsi_id: str | None = None  # SCSI address (H:C:T:L)

    # Sysfs path for SCSI devices
    SCSI_PATH: ClassVar[Path] = Path('/sys/class/scsi_device')

    def __post_init__(self) -> None:
        """Initialize SCSI device.

        - Sets device path if not provided
        - Gets device information from lsscsi
        - Gets model information if not provided

        Raises:
            DeviceNotFoundError: If device does not exist
            DeviceError: If device cannot be accessed
        """
        # Ensure lsscsi is installed
        ensure_installed('lsscsi')

        # Set path based on name if not provided
        if not self.path and self.name:
            self.path = f'/dev/{self.name}'

        # Initialize parent class
        super().__post_init__()

        # Get SCSI ID from lsscsi if not provided
        if not self.scsi_id and self.name:
            result = run(f'lsscsi | grep {self.name} $')
            if result.succeeded:
                with contextlib.suppress(IndexError):
                    # Extract [H:C:T:L] from lsscsi output
                    self.scsi_id = result.stdout.split()[0].strip('[]')

        # Get model from sysfs if not provided
        if not self.model:
            self.model = self.model_name

    @property
    def vendor(self) -> str | None:
        """Get device vendor.

        Reads vendor string from sysfs:
        - Common vendors: ATA, SCSI, USB
        - Helps identify device type and capabilities
        - Used for device-specific handling

        Returns:
            Device vendor or None if not available

        Example:
            ```python
            device.vendor
            'ATA'
            ```
        """
        if not self.scsi_id:
            return None

        try:
            vendor_path = self.SCSI_PATH / self.scsi_id / 'device/vendor'
            return vendor_path.read_text().strip()
        except OSError:
            return None

    @property
    def model_name(self) -> str | None:
        """Get device model name.

        Reads model string from sysfs:
        - Identifies specific device model
        - Contains manufacturer information
        - Used for device compatibility

        Returns:
            Device model name or None if not available

        Example:
            ```python
            device.model_name
            'Samsung SSD 970 EVO'
            ```
        """
        if not self.scsi_id:
            return None

        try:
            model_path = self.SCSI_PATH / self.scsi_id / 'device/model'
            return model_path.read_text().strip()
        except OSError:
            return None

    @property
    def revision(self) -> str | None:
        """Get device revision.

        Reads firmware revision from sysfs:
        - Indicates firmware version
        - Important for bug tracking
        - Used for feature compatibility

        Returns:
            Device revision or None if not available

        Example:
            ```python
            device.revision
            '1.0'
            ```
        """
        if not self.scsi_id:
            return None

        try:
            rev_path = self.SCSI_PATH / self.scsi_id / 'device/rev'
            return rev_path.read_text().strip()
        except OSError:
            return None

    @classmethod
    def get_by_vendor(cls, vendor: str) -> list[ScsiDevice]:
        """Get list of SCSI devices by vendor.

        Uses lsscsi to find devices:
        - Lists all SCSI devices
        - Filters by vendor string
        - Creates device objects

        Args:
            vendor: Device vendor (e.g. 'ATA', 'SCSI')

        Returns:
            List of ScsiDevice instances

        Example:
            ```python
            ScsiDevice.get_by_vendor('ATA')
            [ScsiDevice(name='sda', ...), ScsiDevice(name='sdb', ...)]
            ```
        """
        # Ensure lsscsi is installed
        ensure_installed('lsscsi')
        devices: list[ScsiDevice] = []

        # List SCSI devices using lsscsi
        result = run('lsscsi')
        if result.failed:
            logging.warning('Failed to list SCSI devices')
            return devices

        # Parse lsscsi output
        # Format: [H:C:T:L] type vendor model rev device
        for line in result.stdout.splitlines():
            if vendor not in line:
                continue

            # Parse device info from line
            try:
                parts = line.strip().split()
                scsi_id = parts[0].strip('[]')  # Remove [] from SCSI ID
                name = parts[-1].split('/')[-1]  # Get device name from path

                devices.append(
                    cls(
                        name=name,  # Device name (e.g. sda)
                        scsi_id=scsi_id,  # SCSI ID (e.g. 0:0:0:0)
                    )
                )
            except (IndexError, ValueError):
                logging.warning('Failed to parse device info')
                continue

        return devices
