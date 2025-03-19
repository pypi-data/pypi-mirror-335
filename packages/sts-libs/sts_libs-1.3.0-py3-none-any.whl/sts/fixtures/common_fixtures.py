"""Common test fixtures.

This module provides fixtures that can be used across different test suites:
- Virtual block devices (loop, scsi_debug)
- System resources
- Common utilities

Fixture Dependencies:
1. loop_devices
   - Independent fixture
   - Creates temporary loop devices
   - Handles cleanup automatically

2. scsi_debug_devices
   - Independent fixture
   - Creates SCSI debug devices
   - Handles cleanup automatically

Common Usage:

1. Basic device testing:
   ```
   def test_single_device(loop_devices):
       device = loop_devices[0]
       # Test with single device
   ```

2. Multi-device testing:
   ```
   @pytest.mark.parametrize('loop_devices', [2], indirect=True)
   def test_multiple_devices(loop_devices):
       dev1, dev2 = loop_devices
       # Test with multiple devices
   ```

3. SCSI debug testing:
   ```
   @pytest.mark.parametrize('scsi_debug_devices', [2], indirect=True)
   def test_scsi_devices(scsi_debug_devices):
       dev1, dev2 = scsi_debug_devices
       # Test with SCSI debug devices
   ```

Error Handling:
- Device creation failures skip the test
- Cleanup runs even if test fails
- Resource limits are checked
"""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import logging
from os import getenv
from typing import TYPE_CHECKING

import pytest

from sts.blockdevice import filter_devices_by_block_sizes, get_free_disks
from sts.loop import LoopDevice
from sts.multipath import MultipathDevice, MultipathService
from sts.scsi_debug import ScsiDebugDevice
from sts.target import cleanup_loopback_devices, create_loopback_devices
from sts.utils.syscheck import check_all

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

    from sts.dm import DmDevice


@pytest.fixture(scope='class', autouse=True)
def _log_check() -> Generator[None, None, None]:
    """Perform system checks before and after test execution."""
    assert check_all()
    yield
    assert check_all()


@pytest.fixture
def loop_devices(request: pytest.FixtureRequest) -> Generator[list[str], None, None]:
    """Create loop devices for testing.

    Creates virtual block devices using the loop driver:
    - Each device is 1GB in size
    - Devices are sparse (only allocate used space)
    - Devices are automatically cleaned up
    - Supports multiple devicesce(loop_devices): assert len(loop_devices) == 1 assert loop_d per test

    Configuration:
    - count: Number of devices to create (default: 1)
      Set via parametrize: @pytest.mark.parametrize('loop_devices', [2])

    Error Handling:
    - Skips test if device creation fails
    - Cleans up any created devices on failure
    - Validates device paths before yielding

    Args:
        request: Pytest fixture request with 'count' parameter

    Yields:
        List of loop device paths (e.g. ['/dev/loop0', '/dev/loop1'])

    Example:
        # Single device
        ```python
        def test_device(loop_devices):
            assert len(loop_devices) == 1
            assert loop_devices[0].startswith('/dev/loop')
        ```
        # Multiple devices
        ```
        @pytest.mark.parametrize('loop_devices', [2], indirect=True)
            def test_devices(loop_devices):
                assert len(loop_devices) == 2
                assert all(d.startswith('/dev/loop') for d in loop_devices)
        ```
    """
    count = getattr(request, 'param', 1)  # Default to 1 device if not specified
    devices = []

    # Create devices one by one
    for _ in range(count):
        device = LoopDevice.create(size_mb=1024)
        if not device:
            # Clean up any created devices
            for dev in devices:
                dev.remove()
            pytest.skip(f'Failed to create loop device {len(devices) + 1} of {count}')
        devices.append(device)

    # Yield device paths
    yield [str(dev.device_path) for dev in devices]

    # Clean up
    for device in devices:
        device.remove()


@pytest.fixture
def scsi_debug_devices(request: pytest.FixtureRequest) -> Generator[list[str], None, None]:
    """Create SCSI debug devices for testing.

    Creates virtual SCSI devices using the scsi_debug module:
    - Each device is 1GB in size
    - Devices share a single scsi_debug instance
    - Devices are automatically cleaned up
    - Supports multiple devices per test

    Configuration:
    - count: Number of devices to create (default: 1)
      Set via parametrize: @pytest.mark.parametrize('scsi_debug_devices', [2])

    Error Handling:
    - Skips test if module loading fails
    - Skips test if device creation fails
    - Cleans up module and devices on failure
    - Validates device count before yielding

    Args:
        request: Pytest fixture request with 'count' parameter

    Yields:
        List of SCSI device paths (e.g. ['/dev/sda', '/dev/sdb'])

    Example:
        ```python
        # Single device
        def test_device(scsi_debug_devices):
            assert len(scsi_debug_devices) == 1
            assert scsi_debug_devices[0].startswith('/dev/sd')


        # Multiple devices
        @pytest.mark.parametrize('scsi_debug_devices', [2], indirect=True)
        def test_devices(scsi_debug_devices):
            assert len(scsi_debug_devices) == 2
            assert all(d.startswith('/dev/sd') for d in scsi_debug_devices)
        ```
    """
    count = getattr(request, 'param', 1)  # Default to 1 device if not specified
    logging.info(f'Creating {count} scsi_debug devices')

    # Create SCSI debug device with specified number of targets
    device = ScsiDebugDevice.create(
        size=1024 * 1024 * 1024,  # 1GB
        options=f'num_tgts={count} add_host={count}',
    )
    if not device:
        pytest.skip('Failed to create SCSI debug device')

    # Get all SCSI debug devices
    devices = ScsiDebugDevice.get_devices()
    if not devices or len(devices) < count:
        device.remove()
        pytest.skip(f'Expected {count} SCSI debug devices, got {len(devices or [])}')

    # Yield device paths
    yield [f'/dev/{dev}' for dev in devices[:count]]

    # Clean up
    device.remove()


def _ensure_minimum_devices_base(
    min_devices: int | None = None, *, filter_by_block_size: bool = False, default_block_size: int = 4096
) -> Generator:
    """Base fixture function to ensure minimum number of devices are available.

    Args:
        min_devices: Minimum number of devices required. If None, reads from ENV.
        filter_by_block_size: Whether to filter devices by block size
        default_block_size: Default block size to use for loopback devices if no devices available

    Yields:
        List of device names with '/dev/' prefix
    """
    min_devices = min_devices or int(getenv('MIN_DEVICES', '5'))

    if filter_by_block_size:
        block_sizes, available_devices = filter_devices_by_block_sizes(
            get_free_disks(), prefer_matching_block_sizes=True
        )
        # If there are no devices available, block size is 0
        # Use default_block_size when this happens
        if block_sizes and block_sizes[0] == 0:
            block_sizes = (default_block_size, default_block_size)
        block_size = block_sizes[0] if block_sizes else default_block_size
    else:
        available_devices = [str(dev.path) for dev in get_free_disks()]
        block_size = default_block_size

    if len(available_devices) >= min_devices:
        yield available_devices
    else:
        additional_devices_needed = min_devices - len(available_devices)
        if filter_by_block_size:
            loopback_devices = create_loopback_devices(additional_devices_needed, block_size)
        else:
            loopback_devices = create_loopback_devices(additional_devices_needed)

        logging.info(loopback_devices)
        all_devices = available_devices + loopback_devices
        yield all_devices

        # Cleanup loopback devices
        cleanup_loopback_devices(loopback_devices)


@pytest.fixture
def ensure_minimum_devices_with_same_block_sizes() -> Generator:
    """Fixture that ensures minimum number of devices with same block sizes."""
    yield from _ensure_minimum_devices_base(filter_by_block_size=True)


@pytest.fixture
def ensure_minimum_devices() -> Generator:
    """Fixture that ensures minimum number of devices without block size filtering."""
    yield from _ensure_minimum_devices_base(filter_by_block_size=False)


@pytest.fixture(scope='class')
def multipath_setup() -> Generator[Sequence[DmDevice], None, None]:
    """Fixture to set up and tear down multipath devices for testing.

    This fixture performs the following steps:
    1. Checks if the multipath service is running.
    2. If not running, starts the multipath service.
    3. Retrieves all multipath devices.
    4. Yields the list of multipath devices for use in tests.
    5. Stops the multipath service if it was started by this fixture.

    Yields:
        list[MultipathDevice]: A list of multipath devices available for testing.
    """
    mp_service = MultipathService()
    if not mp_service.is_running():
        mp_service.start()
        devices = MultipathDevice.get_all()
        yield devices
        mp_service.stop()
    else:
        yield MultipathDevice.get_all()
