"""Test Stratis pool management.

This module tests:
- Pool creation and destruction
- Pool operations (start/stop)
- Pool encryption (keyring, tang, tpm2)
- Pool cache and data devices
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from os import getenv

import pytest

from sts.stratis.errors import StratisError
from sts.stratis.pool import PoolCreateConfig, StratisPool
from sts.utils.system import SystemManager


# TODO: Merge/deduplicate with stratis/basic/
@pytest.mark.usefixtures('_stratis_test')
class TestPool:
    """Test Stratis pool management."""

    def setup_method(self) -> None:
        """Set up test method.

        - Ensure stratisd is running
        """
        system = SystemManager()
        if not system.is_service_running('stratisd') and not system.service_start('stratisd'):
            pytest.skip('Could not start stratisd.service')

    def test_pool_create_destroy(self, setup_stratis_key: str) -> None:
        """Test pool creation and destruction.

        Args:
            setup_stratis_key: Stratis key fixture
        """
        key_desc = setup_stratis_key
        pool_name = getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')
        blockdevs = StratisPool.setup_blockdevices()

        # Test basic creation
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = blockdevs
        assert pool.create()
        assert pool.destroy()

        # Test creation with overprovisioning disabled
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = blockdevs
        config = PoolCreateConfig(no_overprovision=True)
        assert pool.create(config)
        assert pool.destroy()

        # Test creation with encryption
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = blockdevs
        config = PoolCreateConfig(key_desc=key_desc)
        assert pool.create(config)
        assert pool.destroy()

        # Test creation with encryption and overprovisioning disabled
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = blockdevs
        config = PoolCreateConfig(key_desc=key_desc, no_overprovision=True)
        assert pool.create(config)
        assert pool.destroy()

    def test_pool_operations(self) -> None:
        """Test pool operations."""
        pool_name = getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')
        blockdevs = StratisPool.setup_blockdevices()

        # Create pool for testing
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = blockdevs
        assert pool.create()

        # Test start/stop
        assert pool.stop()
        assert pool.start()

        # Test start/stop by UUID
        uuid = pool.get_pool_uuid()
        assert uuid is not None
        pool.uuid = uuid
        assert pool.stop()
        assert pool.start()

        # Cleanup
        assert pool.destroy()

    def test_pool_devices(self) -> None:
        """Test pool device operations."""
        pool_name = getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')
        blockdevs = StratisPool.setup_blockdevices()

        # Create pool for testing with first device
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = [blockdevs[0]]
        assert pool.create()

        # Test adding data devices
        assert pool.add_data(blockdevs[1:])

        # Test initializing cache with new devices
        cache_devs = StratisPool.setup_blockdevices()
        assert pool.init_cache(cache_devs[:1])

        # Test adding more cache devices
        assert pool.add_cache(cache_devs[1:])

        # Cleanup
        assert pool.destroy()

    def test_pool_encryption(self, setup_stratis_key: str) -> None:
        """Test pool encryption operations.

        Args:
            setup_stratis_key: Stratis key fixture
        """
        key_desc = setup_stratis_key
        pool_name = getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')
        blockdevs = StratisPool.setup_blockdevices()

        # Test keyring encryption
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = blockdevs
        config = PoolCreateConfig(key_desc=key_desc)
        assert pool.create(config)
        assert pool.stop()
        assert pool.start(unlock_method='keyring')
        assert pool.destroy()

        # Test Tang encryption
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = blockdevs
        config = PoolCreateConfig(
            clevis='tang',
            tang_url='http://tang.example.com',
            thumbprint='abc123',
            trust_url=True,
        )
        assert pool.create(config)
        assert pool.stop()
        assert pool.start(unlock_method='tang')
        assert pool.destroy()

        # Test TPM2 encryption
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = blockdevs
        config = PoolCreateConfig(clevis='tpm2')
        assert pool.create(config)
        assert pool.stop()
        assert pool.start(unlock_method='tpm2')
        assert pool.destroy()

    def test_error_handling(self) -> None:
        """Test error handling."""
        pool_name = getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')
        blockdevs = StratisPool.setup_blockdevices()

        # Test missing name
        pool = StratisPool()
        pool.blockdevs = blockdevs
        assert not pool.create()

        # Test missing devices
        pool = StratisPool()
        pool.name = pool_name
        with pytest.raises(StratisError, match='No block devices provided'):
            pool.create()

        # Test invalid devices
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = ['/dev/nonexistent']
        assert not pool.create()

        # Test operations on non-existent pool
        pool = StratisPool()
        pool.name = 'sts-stratis-test-nonexistent'
        assert not pool.destroy()
        assert not pool.stop()
        assert not pool.start()
        assert not pool.add_data(['/dev/sdc'])
        assert not pool.init_cache(['/dev/nvme0n1'])
        assert not pool.add_cache(['/dev/nvme0n2'])
