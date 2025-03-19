"""LVM test fixtures.

This module provides fixtures for testing LVM (Logical Volume Management):
- Package installation and cleanup
- Service management
- Device configuration
- VDO (Virtual Data Optimizer) support

Fixture Dependencies:
1. _lvm_test (base fixture)
   - Installs LVM packages
   - Manages volume cleanup
   - Logs system information

2. _vdo_test (depends on _lvm_test)
   - Installs VDO packages
   - Manages kernel module
   - Provides data reduction features

Common Usage:
1. Basic LVM testing:
   @pytest.mark.usefixtures('_lvm_test')
   def test_lvm():
       # LVM utilities are installed
       # Volumes are cleaned up after test

2. VDO-enabled testing:
   @pytest.mark.usefixtures('_vdo_test')
   def test_vdo():
       # VDO module is loaded
       # Data reduction is available

Error Handling:
- Package installation failures fail the test
- Module loading failures fail the test
- Volume cleanup runs even if test fails
- Service issues are logged
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

import logging
from os import getenv
from typing import TYPE_CHECKING

import pytest

from sts import lvm
from sts.utils.cmdline import run
from sts.utils.system import SystemManager

if TYPE_CHECKING:
    from collections.abc import Generator

    from sts.blockdevice import BlockDevice

# Constants
LVM_PACKAGE_NAME = 'lvm2'
VDO_PACKAGE_NAME = 'vdo'


@pytest.fixture(scope='class')
def _lvm_test() -> Generator:
    """Set up LVM environment.

    This fixture provides the foundation for LVM testing:
    - Installs LVM utilities (lvm2 package)
    - Logs system information for debugging
    - Cleans up volumes before and after test
    - Ensures consistent test environment

    Package Installation:
    - lvm2: Core LVM utilities
    - Required device-mapper modules

    Volume Cleanup:
    1. Deactivates all volume groups
    2. Removes all physical volumes
    3. Runs before and after each test class
    4. Handles force removal if needed

    System Information:
    - Kernel version
    - LVM version
    - Device-mapper status

    Example:
        ```python
        @pytest.mark.usefixtures('_lvm_test')
        def test_lvm():
            # Create and test LVM volumes
            # Volumes are automatically cleaned up
        ```
    """
    system = SystemManager()
    assert system.package_manager.install(LVM_PACKAGE_NAME)
    logging.info(f'Kernel version: {system.info.kernel}')

    # Clean up existing volumes
    run('vgchange -an')  # Deactivate all VGs
    run('pvremove -ff -y $(pvs -o pv_name --noheadings 2>/dev/null)')  # Remove all PVs

    yield

    # Clean up volumes
    run('vgchange -an')  # Deactivate all VGs
    run('pvremove -ff -y $(pvs -o pv_name --noheadings 2>/dev/null)')  # Remove all PVs


@pytest.fixture(scope='class')
def _vdo_test(_lvm_test: None) -> Generator:
    """Set up VDO environment.

    Args:
       _lvm_test: LVM test fixture required for VDO functionality

    Features:
       - Deduplication, compression, thin provisioning
       - Automatic module loading/unloading
       - Cleanup of VDO resources

    Example:
       @pytest.mark.usefixtures('_vdo_test')
       def test_vdo():
           # Test VDO functionality
           pass
    """
    system = SystemManager()
    assert system.package_manager.install(VDO_PACKAGE_NAME)
    k_version = system.info.kernel
    # if we can't get kernel version, just try to load dm-vdo
    if k_version:
        k_version = k_version.split('.')
        # dm-vdo is available from kernel 6.9, for older version it's available
        # from kmod-kvdo package
        if int(k_version[0]) < 6 and int(k_version[1]) <= 8:
            logging.info('Using kmod-kvdo')
            assert system.package_manager.install('kmod-kvdo')
            # Load module
            result = run('modprobe kvdo')
            assert result.succeeded, 'Failed to load KVDO'
            yield

    result = run('modprobe dm-vdo')
    assert result.succeeded, 'Failed to load dm-vdo'

    yield

    # Unload module
    run('modprobe -r kvdo')
    run('modprobe -r dm-vdo')


@pytest.fixture
def setup_vg(ensure_minimum_devices_with_same_block_sizes: list[BlockDevice]) -> Generator[str, None, None]:
    """Set up an LVM Volume Group (VG) with Physical Volumes (PVs) for testing.

    This fixture creates a Volume Group using the provided block devices. It handles the creation
    of Physical Volumes from the block devices and ensures proper cleanup after tests, even if
    they fail.

    Args:
        ensure_minimum_devices_with_same_block_sizes: List of BlockDevice objects with matching
            block sizes to be used for creating Physical Volumes.

    Yields:
        str: Name of the created Volume Group.

    Raises:
        AssertionError: If PV creation fails for any device.

    Example:
        def test_volume_group(setup_vg):
            vg_name = setup_vg
            # Use vg_name in your test...
    """
    vg_name = getenv('STS_VG_NAME', 'stsvg0')
    pvs = []

    try:
        # Create PVs
        for device in ensure_minimum_devices_with_same_block_sizes:
            device_name = str(device.path).replace('/dev/', '')
            device_path = str(device.path)

            pv = lvm.PhysicalVolume(name=device_name, path=device_path)
            assert pv.create(), f'Failed to create PV on device {device_path}'
            pvs.append(pv)

        # Create VG
        vg = lvm.VolumeGroup(name=vg_name, pvs=[pv.path for pv in pvs])
        assert vg.create(), f'Failed to create VG {vg_name}'

        yield vg_name

    finally:
        # Cleanup in reverse order
        vg = lvm.VolumeGroup(name=vg_name)
        if not vg.remove():
            logging.warning(f'Failed to remove VG {vg_name}')

        for pv in pvs:
            if not pv.remove():
                logging.warning(f'Failed to remove PV {pv.path}')
