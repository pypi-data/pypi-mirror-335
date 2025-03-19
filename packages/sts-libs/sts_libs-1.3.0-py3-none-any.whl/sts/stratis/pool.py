"""Stratis pool management.

This module provides functionality for managing Stratis pools:
- Pool creation
- Pool operations
- Pool encryption
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, ClassVar, Literal

import pytest

from sts.stratis.base import StratisBase, StratisConfig, StratisOptions
from sts.stratis.errors import StratisPoolError
from sts.utils.cmdline import run

# Type aliases
EncryptionType = Literal['keyring', 'tang', 'tpm2']


@dataclass
class BlockDevInfo:
    """Block device information from stratis report.

    Args:
        path: Device path
        size: Device size in sectors
        uuid: Device UUID
        in_use: Whether device is in use
        blksizes: Block size information
    """

    path: str | None = None
    size: str | None = None
    uuid: str | None = None
    in_use: bool = False
    blksizes: str | None = None

    @staticmethod
    def parse_bool(value: bool | int | str | None) -> bool:
        """Parse boolean value from stratis output.

        Args:
            value: Value to parse (can be bool, int, str, or None)

        Returns:
            Parsed boolean value
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BlockDevInfo:
        """Create device info from dictionary.

        Args:
            data: Dictionary data

        Returns:
            BlockDevInfo instance
        """
        return cls(
            path=data.get('path'),
            size=data.get('size'),
            uuid=data.get('uuid'),
            in_use=cls.parse_bool(data.get('in_use')),
            blksizes=data.get('blksizes'),
        )


@dataclass
class BlockDevs:
    """Block devices from stratis report.

    Args:
        datadevs: List of data devices
        cachedevs: List of cache devices
    """

    datadevs: list[BlockDevInfo] = field(default_factory=list)
    cachedevs: list[BlockDevInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BlockDevs:
        """Create block devices from dictionary.

        Args:
            data: Dictionary data

        Returns:
            BlockDevs instance
        """
        return cls(
            datadevs=[BlockDevInfo.from_dict(dev) for dev in data.get('datadevs', [])],
            cachedevs=[BlockDevInfo.from_dict(dev) for dev in data.get('cachedevs', [])],
        )


@dataclass
class PoolReport:
    """Pool report data.

    Args:
        name: Pool name (optional, discovered from system)
        blockdevs: Block devices (optional, discovered from system)
        uuid: Pool UUID (optional, discovered from system)
        encryption: Encryption type (optional, discovered from system)
        fs_limit: Filesystem limit (optional)
        available_actions: Available actions (optional)
        filesystems: List of filesystems (optional)

    Example:
        ```python
        report = PoolReport()  # Discovers first available pool
        report = PoolReport(name='pool1')  # Discovers other values
        ```
    """

    name: str | None = None
    blockdevs: BlockDevs = field(default_factory=BlockDevs)
    uuid: str | None = None
    encryption: EncryptionType | None = None
    fs_limit: int | None = None
    available_actions: str | None = None
    filesystems: list[Any] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PoolReport | None:
        """Create report from dictionary.

        Args:
            data: Dictionary data

        Returns:
            PoolReport instance or None if invalid
        """
        try:
            return cls(
                name=data.get('name'),
                blockdevs=BlockDevs.from_dict(data.get('blockdevs', {})),
                uuid=data.get('uuid'),
                encryption=data.get('encryption'),
                fs_limit=data.get('fs_limit'),
                available_actions=data.get('available_actions'),
                filesystems=data.get('filesystems', []),
            )
        except (KeyError, TypeError) as e:
            logging.warning(f'Invalid pool report data: {e}')
            return None


@dataclass
class PoolCreateConfig:
    """Pool creation configuration.

    Args:
        key_desc: Key description for keyring encryption (optional)
        tang_url: Tang server URL for tang encryption (optional)
        thumbprint: Tang server thumbprint (optional)
        clevis: Clevis encryption configuration (optional)
        trust_url: Trust Tang server URL (optional)
        no_overprovision: Disable overprovisioning (optional)

    Example:
        ```python
        config = PoolCreateConfig()  # Uses defaults
        config = PoolCreateConfig(key_desc='mykey')  # Custom settings
        ```
    """

    # Optional parameters
    key_desc: str | None = None
    tang_url: str | None = None
    thumbprint: str | None = None
    clevis: str | None = None
    trust_url: bool = False
    no_overprovision: bool = False


@dataclass
class TangConfig:
    """Tang server configuration.

    Args:
        url: Tang server URL (optional, discovered from system)
        trust_url: Trust server URL (optional)
        thumbprint: Server thumbprint (optional)

    Example:
        ```python
        config = TangConfig()  # Uses defaults
        config = TangConfig(url='http://tang.example.com')  # Custom settings
        ```
    """

    # Optional parameters
    url: str | None = None
    trust_url: bool = False
    thumbprint: str | None = None


@dataclass
class StratisPool(StratisBase):
    """Stratis pool representation.

    This class provides functionality for managing Stratis pools:
    - Pool creation
    - Pool operations
    - Pool encryption

    Args:
        name: Pool name (optional, discovered from system)
        uuid: Pool UUID (optional, discovered from system)
        encryption: Encryption type (optional, discovered from system)
        blockdevs: List of block devices (optional, discovered from system)

    Example:
        ```python
        pool = StratisPool()  # Discovers first available pool
        pool = StratisPool(name='pool1')  # Discovers other values
        ```
    """

    name: str | None = None
    uuid: str | None = None
    encryption: EncryptionType | None = None
    blockdevs: list[str] = field(default_factory=list)

    # Class-level paths
    POOL_PATH: ClassVar[str] = '/stratis/pool'

    def __post_init__(self) -> None:
        """Initialize pool."""
        # Initialize base class with default config
        super().__init__(config=StratisConfig())

        # Discover pool info if needed
        if not self.uuid or not self.encryption or not self.blockdevs:
            result = self.run_command('report')
            if result.succeeded and result.stdout:
                try:
                    report = json.loads(result.stdout)
                    if not isinstance(report, dict):
                        logging.warning('Invalid report format: not a dictionary')
                        return

                    pools = report.get('pools', [])
                    if not isinstance(pools, list):
                        logging.warning('Invalid pools format: not a list')
                        return

                    for pool in pools:
                        if not isinstance(pool, dict):
                            logging.warning('Invalid pool format: not a dictionary')
                            continue

                        if not self.name or self.name == pool.get('name'):
                            if not self.name:
                                self.name = pool.get('name')
                            if not self.uuid:
                                self.uuid = pool.get('uuid')
                            if not self.encryption:
                                self.encryption = pool.get('encryption')
                            if not self.blockdevs:
                                blockdevs = pool.get('blockdevs', {})
                                if not isinstance(blockdevs, dict):
                                    logging.warning('Invalid blockdevs format: not a dictionary')
                                    continue

                                # Get paths from both data and cache devices
                                self.blockdevs = [
                                    path
                                    for dev in blockdevs.get('datadevs', [])
                                    if isinstance(dev, dict) and (path := dev.get('path'))
                                ] + [
                                    path
                                    for dev in blockdevs.get('cachedevs', [])
                                    if isinstance(dev, dict) and (path := dev.get('path'))
                                ]
                            break
                except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
                    logging.warning(f'Failed to parse pool info: {e}')

    def get_pool_uuid(self) -> str | None:
        """Get pool UUID.

        Returns:
            Pool UUID or None if not found

        Example:
            ```python
            pool.get_pool_uuid()
            '123e4567-e89b-12d3-a456-426614174000'
            ```
        """
        if not self.name:
            return None

        result = self.run_command('report')
        if result.failed or not result.stdout:
            return None

        try:
            report = json.loads(result.stdout)
            for pool in report['pools']:
                if self.name == pool['name']:
                    return pool['uuid']
        except (KeyError, ValueError) as e:
            logging.warning(f'Failed to get pool UUID: {e}')

        return None

    def create(self, config: PoolCreateConfig | None = None) -> bool:
        """Create pool.

        Args:
            config: Pool creation configuration

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.create(PoolCreateConfig(key_desc='mykey'))
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        if not self.blockdevs:
            raise StratisPoolError('No block devices specified')

        options: StratisOptions = {}
        if config:
            if config.key_desc:
                options['--key-desc'] = config.key_desc
            if config.clevis:
                options['--clevis'] = config.clevis
            if config.tang_url:
                options['--tang-url'] = config.tang_url
            if config.thumbprint:
                options['--thumbprint'] = config.thumbprint
            if config.trust_url:
                options['--trust-url'] = None
            if config.no_overprovision:
                options['--no-overprovision'] = None

        result = self.run_command(
            subcommand='pool',
            action='create',
            options=options,
            positional_args=[self.name, ' '.join(self.blockdevs)],
        )
        return not result.failed

    def destroy(self) -> bool:
        """Destroy pool.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.destroy()
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='destroy',
            positional_args=[self.name],
        )
        return not result.failed

    def start(self, unlock_method: EncryptionType | None = None) -> bool:
        """Start pool.

        Args:
            unlock_method: Encryption unlock method

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.start(unlock_method='keyring')
            True
            ```
        """
        if not self.name and not self.uuid:
            logging.error('Pool name or UUID required')
            return False

        options: StratisOptions = {}
        if unlock_method:
            options['--unlock-method'] = unlock_method
        if self.uuid:
            options['--uuid'] = self.uuid
        else:
            options['--name'] = self.name

        result = self.run_command('pool', action='start', options=options)
        return not result.failed

    def stop(self) -> bool:
        """Stop pool.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.stop()
            True
            ```
        """
        if not self.name and not self.uuid:
            logging.error('Pool name or UUID required')
            return False

        options: StratisOptions = {}
        if self.uuid:
            options['--uuid'] = self.uuid
        else:
            options['--name'] = self.name

        result = self.run_command('pool', action='stop', options=options)
        return not result.failed

    def add_data(self, blockdevs: list[str]) -> bool:
        """Add data devices to pool.

        Args:
            blockdevs: List of block devices

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.add_data(['/dev/sdd', '/dev/sde'])
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='add-data',
            positional_args=[self.name, ' '.join(blockdevs)],
        )
        if not result.failed:
            self.blockdevs.extend(blockdevs)
        return not result.failed

    def init_cache(self, blockdevs: list[str]) -> bool:
        """Initialize cache devices.

        Args:
            blockdevs: List of block devices

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.init_cache(['/dev/nvme0n1'])
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        # Pass each device as a separate argument
        result = self.run_command(
            subcommand='pool',
            action='init-cache',
            positional_args=[self.name, *blockdevs],
        )
        if result.failed:
            logging.error(f'Failed to initialize cache: {result.stderr}')
        return not result.failed

    def add_cache(self, blockdevs: list[str]) -> bool:
        """Add cache devices to pool.

        Args:
            blockdevs: List of block devices

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.add_cache(['/dev/nvme0n2'])
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='add-cache',
            positional_args=[self.name, ' '.join(blockdevs)],
        )
        return not result.failed

    def bind_keyring(self, key_desc: str) -> bool:
        """Bind pool to keyring.

        Args:
            key_desc: Key description

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.bind_keyring('mykey')
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='bind keyring',
            positional_args=[self.name, key_desc],
        )
        if not result.failed:
            self.encryption = 'keyring'
        return not result.failed

    def bind_tang(self, config: TangConfig) -> bool:
        """Bind pool to Tang server.

        Args:
            config: Tang server configuration

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.bind_tang(TangConfig('http://tang.example.com'))
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        if not config.url:
            logging.error('Tang server URL required')
            return False

        options: StratisOptions = {}
        if config.trust_url:
            options['--trust-url'] = None
        if config.thumbprint:
            options['--thumbprint'] = config.thumbprint

        result = self.run_command(
            subcommand='pool',
            action='bind tang',
            options=options,
            positional_args=[self.name, config.url],
        )
        if not result.failed:
            self.encryption = 'tang'
        return not result.failed

    def bind_tpm2(self) -> bool:
        """Bind pool to TPM2.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.bind_tpm2()
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='bind tpm2',
            positional_args=[self.name],
        )
        if not result.failed:
            self.encryption = 'tpm2'
        return not result.failed

    def unbind_keyring(self) -> bool:
        """Unbind pool from keyring.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.unbind_keyring()
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='unbind keyring',
            positional_args=[self.name],
        )
        if not result.failed:
            self.encryption = None
        return not result.failed

    def unbind_clevis(self) -> bool:
        """Unbind pool from Clevis.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.unbind_clevis()
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='unbind clevis',
            positional_args=[self.name],
        )
        if not result.failed:
            self.encryption = None
        return not result.failed

    @classmethod
    def from_report(cls, report: PoolReport) -> StratisPool | None:
        """Create pool from report.

        Args:
            report: Pool report data

        Returns:
            StratisPool instance or None if invalid

        Example:
            ```python
            pool = StratisPool.from_report(report)
            ```
        """
        if not report.name:
            return None

        # Get paths from both data and cache devices
        paths = [dev.path for dev in report.blockdevs.datadevs if dev.path] + [
            dev.path for dev in report.blockdevs.cachedevs if dev.path
        ]

        return cls(
            name=report.name,
            uuid=report.uuid,
            encryption=report.encryption,
            blockdevs=paths,
        )

    @classmethod
    def get_all(cls) -> list[StratisPool]:
        """Get all Stratis pools.

        Returns:
            List of StratisPool instances

        Example:
            ```python
            StratisPool.get_all()
            [StratisPool(name='pool1', ...), StratisPool(name='pool2', ...)]
            ```
        """
        pools: list[StratisPool] = []
        # Create base instance without __post_init__
        base = super().__new__(cls)
        super(cls, base).__init__()

        result = base.run_command('report')
        if result.failed or not result.stdout:
            return pools

        try:
            report = json.loads(result.stdout)
            pools.extend(
                pool
                for pool_data in report['pools']
                if (pool := cls.from_report(PoolReport.from_dict(pool_data) or PoolReport())) is not None
            )
        except (KeyError, ValueError) as e:
            logging.warning(f'Failed to parse report: {e}')

        return pools

    @classmethod
    def setup_blockdevices(cls) -> list[str]:
        """Set up block devices for testing.

        Returns:
            List of device paths

        Example:
            ```python
            StratisPool.setup_blockdevices()
            ['/dev/sda', '/dev/sdb']
            ```
        """
        # Get free disks
        from sts.blockdevice import get_free_disks

        blockdevices = get_free_disks()
        if not blockdevices:
            pytest.skip('No free disks found')

        # Group disks by block sizes
        filtered_disks_by_block_sizes: dict[tuple[int, int], list[str]] = {}
        for disk in blockdevices:
            block_sizes = (disk.sector_size, disk.block_size)
            if block_sizes in filtered_disks_by_block_sizes:
                filtered_disks_by_block_sizes[block_sizes].append(str(disk.path))
            else:
                filtered_disks_by_block_sizes[block_sizes] = [str(disk.path)]

        # Find devices with the most common block sizes
        most_common_block_sizes: list[str] = []
        for disks in filtered_disks_by_block_sizes.values():
            if len(disks) > len(most_common_block_sizes):
                most_common_block_sizes = disks

        # Clear start of devices
        for disk in most_common_block_sizes:
            run(f'dd if=/dev/zero of={disk} bs=1M count=10')

        return most_common_block_sizes
