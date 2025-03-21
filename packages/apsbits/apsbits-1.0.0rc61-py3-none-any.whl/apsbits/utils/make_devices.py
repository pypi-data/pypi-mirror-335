"""
Make devices from YAML files
=============================

Construct ophyd-style devices from simple specifications in YAML files.

.. autosummary::
    :nosignatures:

    ~make_devices
    ~Instrument
"""

import logging
import pathlib
import sys
import time

import guarneri
from apstools.plans import run_blocking_function
from apstools.utils import dynamic_import
from bluesky import plan_stubs as bps

from apsbits.utils.aps_functions import host_on_aps_subnet
from apsbits.utils.config_loaders import get_config
from apsbits.utils.config_loaders import load_config_yaml
from apsbits.utils.controls_setup import oregistry  # noqa: F401

logger = logging.getLogger(__name__)
logger.bsdev(__file__)


def make_devices(*, pause: float = 1):
    """
    (plan stub) Create the ophyd-style controls for this instrument.

    Feel free to modify this plan to suit the needs of your instrument.

    EXAMPLE::

        RE(make_devices())

    PARAMETERS

    pause : float
        Wait 'pause' seconds (default: 1) for slow objects to connect.

    """

    logger.debug("(Re)Loading local control objects.")

    iconfig = get_config()

    instrument_path = pathlib.Path(iconfig.get("INSTRUMENT_PATH")).parent
    configs_path = instrument_path / "configs"
    
    # Get device files and ensure it's a list
    device_files = iconfig.get("DEVICES_FILES", [])
    if isinstance(device_files, str):
        device_files = [device_files]
    logger.debug("Loading device files: %r", device_files)

    # Load each device file
    for device_file in device_files:
        device_path = configs_path / device_file
        if not device_path.exists():
            logger.error(f"Device file not found: {device_path}")
            continue
        logger.info(f"Loading device file: {device_path}")
        try:
            yield from run_blocking_function(
                _loader, device_path, main=True
            )
        except Exception as e:
            logger.error(f"Error loading device file {device_path}: {str(e)}")
            continue

    # Handle APS-specific device files if on APS subnet
    aps_control_devices_files = iconfig.get("APS_DEVICES_FILES", [])
    if isinstance(aps_control_devices_files, str):
        aps_control_devices_files = [aps_control_devices_files]
        
    if aps_control_devices_files and host_on_aps_subnet():
        for device_file in aps_control_devices_files:
            device_path = configs_path / device_file
            if not device_path.exists():
                logger.error(f"APS device file not found: {device_path}")
                continue
            logger.info(f"Loading APS device file: {device_path}")
            try:
                yield from run_blocking_function(
                    _loader, device_path, main=True
                )
            except Exception as e:
                logger.error(f"Error loading APS device file {device_path}: {str(e)}")
                continue

    if pause > 0:
        logger.debug(
            "Waiting %s seconds for slow objects to connect.",
            pause,
        )
        yield from bps.sleep(pause)

    # Configure any of the controls here, or in plan stubs


def _loader(yaml_device_file, main=True):
    """
    Load our ophyd-style controls as described in a YAML file.

    PARAMETERS

    yaml_device_file : str or pathlib.Path
        YAML file describing ophyd-style controls to be created.
    main : bool
        If ``True`` add these devices to the ``__main__`` namespace.

    """
    logger.debug("Devices file %r.", str(yaml_device_file))
    t0 = time.time()
    _instr.load(yaml_device_file)
    logger.info("Devices loaded in %.3f s.", time.time() - t0)

    if main:
        main_namespace = sys.modules["__main__"]
        for label in oregistry.device_names:
            logger.info(f"Setting up {label} in main namespace")
            setattr(main_namespace, label, oregistry[label])


class Instrument(guarneri.Instrument):
    """Custom YAML loader for guarneri."""

    def parse_yaml_file(self, config_file: pathlib.Path | str) -> list[dict]:
        """Read device configurations from YAML format file."""
        if isinstance(config_file, str):
            config_file = pathlib.Path(config_file)

        def parser(creator, specs):
            if creator not in self.device_classes:
                self.device_classes[creator] = dynamic_import(creator)
            entries = [
                {
                    "device_class": creator,
                    "args": (),  # ALL specs are kwargs!
                    "kwargs": table,
                }
                for table in specs
            ]
            return entries

        devices = [
            device
            # parse the file
            for k, v in load_config_yaml(config_file).items()
            # each support type (class, factory, function, ...)
            for device in parser(k, v)
        ]
        return devices


_instr = Instrument({}, registry=oregistry)  # singleton
