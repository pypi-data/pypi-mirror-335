"""Unit tests for Stratis pool management.

This module tests:
- BlockDevInfo parsing
- BlockDevs handling
- Pool report parsing
- Pool configuration
- Pool operations
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any

import pytest

from sts.stratis.pool import (
    BlockDevInfo,
    BlockDevs,
    PoolCreateConfig,
    PoolReport,
    StratisPool,
    TangConfig,
)


class TestBlockDevInfo:
    """Test BlockDevInfo class."""

    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            (True, True),
            (False, False),
            (1, True),
            (0, False),
            ('true', True),
            ('false', False),
            ('1', True),
            ('0', False),
            ('yes', True),
            ('no', False),
            ('on', True),
            ('off', False),
            (None, False),
            ('invalid', False),
        ],
    )
    def test_parse_bool(self, value: Any, expected: bool) -> None:
        """Test boolean value parsing."""
        assert BlockDevInfo.parse_bool(value) == expected

    def test_from_dict(self) -> None:
        """Test creating device info from dictionary."""
        data = {
            'path': '/dev/sda',
            'size': '1000000',
            'uuid': '123e4567-e89b-12d3-a456-426614174000',
            'in_use': True,
            'blksizes': '512/4096',
        }
        dev = BlockDevInfo.from_dict(data)
        assert dev.path == '/dev/sda'
        assert dev.size == '1000000'
        assert dev.uuid == '123e4567-e89b-12d3-a456-426614174000'
        assert dev.in_use is True
        assert dev.blksizes == '512/4096'

    def test_from_dict_missing_fields(self) -> None:
        """Test creating device info with missing fields."""
        data = {'path': '/dev/sda'}
        dev = BlockDevInfo.from_dict(data)
        assert dev.path == '/dev/sda'
        assert dev.size is None
        assert dev.uuid is None
        assert dev.in_use is False
        assert dev.blksizes is None


class TestBlockDevs:
    """Test BlockDevs class."""

    def test_from_dict(self) -> None:
        """Test creating block devices from dictionary."""
        data = {
            'datadevs': [
                {'path': '/dev/sda', 'in_use': True},
                {'path': '/dev/sdb', 'in_use': False},
            ],
            'cachedevs': [
                {'path': '/dev/nvme0n1', 'in_use': True},
            ],
        }
        devs = BlockDevs.from_dict(data)
        assert len(devs.datadevs) == 2
        assert len(devs.cachedevs) == 1
        assert devs.datadevs[0].path == '/dev/sda'
        assert devs.datadevs[0].in_use is True
        assert devs.datadevs[1].path == '/dev/sdb'
        assert devs.datadevs[1].in_use is False
        assert devs.cachedevs[0].path == '/dev/nvme0n1'
        assert devs.cachedevs[0].in_use is True

    def test_from_dict_empty(self) -> None:
        """Test creating block devices from empty dictionary."""
        data = {}
        devs = BlockDevs.from_dict(data)
        assert len(devs.datadevs) == 0
        assert len(devs.cachedevs) == 0


class TestPoolReport:
    """Test PoolReport class."""

    def test_from_dict(self) -> None:
        """Test creating pool report from dictionary."""
        data = {
            'name': 'pool1',
            'blockdevs': {
                'datadevs': [{'path': '/dev/sda'}],
                'cachedevs': [{'path': '/dev/nvme0n1'}],
            },
            'uuid': '123e4567-e89b-12d3-a456-426614174000',
            'encryption': 'keyring',
            'fs_limit': 10,
            'available_actions': 'add-data',
            'filesystems': [{'name': 'fs1'}],
        }
        report = PoolReport.from_dict(data)
        assert report is not None
        assert report.name == 'pool1'
        assert len(report.blockdevs.datadevs) == 1
        assert len(report.blockdevs.cachedevs) == 1
        assert report.uuid == '123e4567-e89b-12d3-a456-426614174000'
        assert report.encryption == 'keyring'
        assert report.fs_limit == 10
        assert report.available_actions == 'add-data'
        assert len(report.filesystems) == 1

    def test_from_dict_invalid(self) -> None:
        """Test creating pool report from invalid dictionary."""
        data = {'invalid': 'data'}
        report = PoolReport.from_dict(data)
        assert report is not None
        assert report.name is None
        assert len(report.blockdevs.datadevs) == 0
        assert len(report.blockdevs.cachedevs) == 0
        assert report.uuid is None
        assert report.encryption is None
        assert report.fs_limit is None
        assert report.available_actions is None
        assert len(report.filesystems) == 0


class TestPoolCreateConfig:
    """Test PoolCreateConfig class."""

    def test_defaults(self) -> None:
        """Test default configuration values."""
        config = PoolCreateConfig()
        assert config.key_desc is None
        assert config.tang_url is None
        assert config.thumbprint is None
        assert config.clevis is None
        assert config.trust_url is False
        assert config.no_overprovision is False

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = PoolCreateConfig(
            key_desc='mykey',
            tang_url='http://tang.example.com',
            thumbprint='abc123',
            clevis='tang',
            trust_url=True,
            no_overprovision=True,
        )
        assert config.key_desc == 'mykey'
        assert config.tang_url == 'http://tang.example.com'
        assert config.thumbprint == 'abc123'
        assert config.clevis == 'tang'
        assert config.trust_url is True
        assert config.no_overprovision is True


class TestTangConfig:
    """Test TangConfig class."""

    def test_defaults(self) -> None:
        """Test default configuration values."""
        config = TangConfig()
        assert config.url is None
        assert config.trust_url is False
        assert config.thumbprint is None

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = TangConfig(
            url='http://tang.example.com',
            trust_url=True,
            thumbprint='abc123',
        )
        assert config.url == 'http://tang.example.com'
        assert config.trust_url is True
        assert config.thumbprint == 'abc123'


@pytest.mark.usefixtures('mock_command_result')
class TestStratisPool:
    """Test StratisPool class."""

    def test_init_defaults(self) -> None:
        """Test default pool values."""
        pool = StratisPool()
        assert pool.name is None
        assert pool.uuid is None
        assert pool.encryption is None
        assert len(pool.blockdevs) == 0

    def test_init_custom(self) -> None:
        """Test custom pool values."""
        pool = StratisPool(
            name='pool1',
            uuid='123e4567-e89b-12d3-a456-426614174000',
            encryption='keyring',
            blockdevs=['/dev/sda', '/dev/sdb'],
        )
        assert pool.name == 'pool1'
        assert pool.uuid == '123e4567-e89b-12d3-a456-426614174000'
        assert pool.encryption == 'keyring'
        assert pool.blockdevs == ['/dev/sda', '/dev/sdb']

    def test_create_pool(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test pool creation."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis pool create pool1 /dev/sda /dev/sdb'] = mock_command_result()

        pool = StratisPool(
            name='pool1',
            blockdevs=['/dev/sda', '/dev/sdb'],
        )
        assert pool.create() is True
        assert calls[-1] == 'stratis pool create pool1 /dev/sda /dev/sdb'

    def test_create_pool_with_encryption(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test pool creation with encryption."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis pool create --key-desc mykey pool1 /dev/sda'] = mock_command_result()

        pool = StratisPool(name='pool1', blockdevs=['/dev/sda'])
        config = PoolCreateConfig(key_desc='mykey')
        assert pool.create(config) is True
        assert calls[-1] == 'stratis pool create --key-desc mykey pool1 /dev/sda'

    def test_destroy_pool(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test pool destruction."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis pool destroy pool1'] = mock_command_result()

        pool = StratisPool(name='pool1')
        assert pool.destroy() is True
        assert calls[-1] == 'stratis pool destroy pool1'

    def test_add_data(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test adding data devices."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis pool add-data pool1 /dev/sdc /dev/sdd'] = mock_command_result()

        pool = StratisPool(name='pool1', blockdevs=['/dev/sda', '/dev/sdb'])
        assert pool.add_data(['/dev/sdc', '/dev/sdd']) is True
        assert calls[-1] == 'stratis pool add-data pool1 /dev/sdc /dev/sdd'
        assert pool.blockdevs == ['/dev/sda', '/dev/sdb', '/dev/sdc', '/dev/sdd']

    def test_init_cache(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test initializing cache devices."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis pool init-cache pool1 /dev/nvme0n1'] = mock_command_result()

        pool = StratisPool(name='pool1')
        assert pool.init_cache(['/dev/nvme0n1']) is True
        assert calls[-1] == 'stratis pool init-cache pool1 /dev/nvme0n1'

    def test_bind_keyring(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test binding pool to keyring."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis pool bind keyring pool1 mykey'] = mock_command_result()

        pool = StratisPool(name='pool1')
        assert pool.bind_keyring('mykey') is True
        assert calls[-1] == 'stratis pool bind keyring pool1 mykey'
        assert pool.encryption == 'keyring'

    def test_bind_tang(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test binding pool to Tang server."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis pool bind tang --thumbprint abc123 pool1 http://tang.example.com'] = mock_command_result()

        pool = StratisPool(name='pool1')
        config = TangConfig(url='http://tang.example.com', thumbprint='abc123')
        assert pool.bind_tang(config) is True
        assert calls[-1] == ('stratis pool bind tang --thumbprint abc123 pool1 http://tang.example.com')
        assert pool.encryption == 'tang'

    def test_get_all(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test getting all pools."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(
            stdout="""{
            "pools": [
                {
                    "name": "pool1",
                    "uuid": "123e4567-e89b-12d3-a456-426614174000",
                    "encryption": "keyring",
                    "blockdevs": {
                        "datadevs": [{"path": "/dev/sda"}],
                        "cachedevs": []
                    }
                }
            ]
        }"""
        )

        pools = StratisPool.get_all()
        assert len(pools) == 1
        assert pools[0].name == 'pool1'
        assert pools[0].uuid == '123e4567-e89b-12d3-a456-426614174000'
        assert pools[0].encryption == 'keyring'
        assert pools[0].blockdevs == ['/dev/sda']
        assert calls == ['stratis report']
