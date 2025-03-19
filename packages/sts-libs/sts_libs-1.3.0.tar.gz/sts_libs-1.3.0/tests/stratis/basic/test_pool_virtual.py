"""Test Stratis pool management with virtual devices.

This module tests basic Stratis functionality using:
- Loop devices (file-backed block devices)
- SCSI debug devices (kernel module devices)
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os

import pytest

from sts.stratis.filesystem import StratisFilesystem
from sts.stratis.pool import PoolCreateConfig, StratisPool
from sts.utils.system import SystemManager


@pytest.mark.usefixtures('_stratis_test')
class TestPoolVirtual:
    """Test Stratis pool management with virtual devices."""

    def setup_method(self) -> None:
        """Set up test method.

        - Ensure stratisd is running
        """
        system = SystemManager()
        if not system.is_service_running('stratisd') and not system.service_start('stratisd'):
            pytest.skip('Could not start stratisd.service')

    @pytest.mark.parametrize('loop_devices', [2], indirect=True)
    def test_pool_basic_loop(self, loop_devices: list[str]) -> None:
        """Test basic pool operations with loop devices.

        Args:
            loop_devices: Loop device fixture
        """
        pool_name = os.getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')

        # Test basic creation
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = loop_devices
        assert pool.create()
        assert pool.destroy()

        # Test creation with overprovisioning disabled
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = loop_devices
        config = PoolCreateConfig(no_overprovision=True)
        assert pool.create(config)
        assert pool.destroy()

    @pytest.mark.parametrize('loop_devices', [2], indirect=True)
    def test_pool_encryption(self, loop_devices: list[str], setup_stratis_key: str) -> None:
        """Test pool encryption operations.

        Args:
            loop_devices: Loop device fixture
            setup_stratis_key: Stratis key fixture
        """
        pool_name = os.getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')

        # Create encrypted pool
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = loop_devices
        config = PoolCreateConfig(key_desc=setup_stratis_key)
        assert pool.create(config)

        # Test stop/start with encryption
        assert pool.stop()
        assert pool.start(unlock_method='keyring')

        # Cleanup
        assert pool.destroy()

    @pytest.mark.skip(reason='TODO: Trigger device failure better')
    @pytest.mark.parametrize('scsi_debug_devices', [2], indirect=True)
    def test_pool_failures(self, stratis_failing_pool: StratisPool) -> None:
        """Test pool behavior with failing devices.

        Args:
            stratis_failing_pool: Failing pool fixture
        """
        # The pool is created with a device that fails every other operation
        # Test operations that should fail
        assert not stratis_failing_pool.stop()
        assert not stratis_failing_pool.start()

        # Test operations that should succeed (next operation after failure)
        assert stratis_failing_pool.stop()
        assert stratis_failing_pool.start()

        # Ensure pool is destroyed before scsi_debug devices are removed
        assert stratis_failing_pool.destroy()

    @pytest.mark.parametrize('loop_devices', [2], indirect=True)
    def test_pool_thin_provisioning(self, stratis_test_pool: StratisPool) -> None:
        """Test pool thin provisioning.

        Args:
            stratis_test_pool: Test pool fixture
        """
        # Create filesystem with default size (thin provisioned)
        fs_name = 'sts-stratis-test-fs'
        fs = StratisFilesystem(name=fs_name, pool_name=stratis_test_pool.name)
        assert fs.create()

        # Verify filesystem exists
        filesystems = StratisFilesystem.get_all(pool_name=stratis_test_pool.name)
        assert any(fs.name == fs_name for fs in filesystems)

        # Cleanup
        assert fs.destroy()

    @pytest.mark.skip(reason='TODO: Use multiple devices')
    @pytest.mark.parametrize('scsi_debug_devices', [2], indirect=True)
    def test_pool_cache(self, scsi_debug_devices: list[str]) -> None:
        """Test pool cache operations.

        Args:
            scsi_debug_devices: SCSI debug device fixture (requires  devices)
        """
        pool_name = os.getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')

        # Create pool with first device only
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = [scsi_debug_devices[0]]  # Only use first device for data tier
        assert pool.create()
        logging.info(scsi_debug_devices)

        try:
            # Initialize cache with second device
            assert pool.init_cache([scsi_debug_devices[1]])  # Use second device for cache tier

        finally:
            # Ensure pool is destroyed before scsi_debug devices are removed
            assert pool.destroy()
