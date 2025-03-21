import re
from nidaqmx import Task, system
from nidaqmx.constants import AcquisitionType
from InstruHub.instrument.base import Instrument


class NiDaq(Instrument):
    """
    Class to manage an NI DAQ device.

    Parameters
    ----------
    name : str
        Identifier for this instrument instance.
    channel : str, optional
        The NI channel to use (e.g., "Dev1/ai0"), by default "Dev1/ai0".
    sample_rate : int, optional
        Sampling rate in samples per second, by default 1000.
    samples_per_channel : int, optional
        Number of samples to acquire per read, by default 1000.
    min_val : float, optional
        Minimum voltage value expected, by default -10.0.
    max_val : float, optional
        Maximum voltage value expected, by default 10.0.
    config : dict, optional
        Optional configuration dictionary, by default None.
    """

    def __init__(self,
        name,
        channel="Dev1/ai0",
        sample_rate=1000,
        samples_per_channel=1000,
        min_val=-10.0,
        max_val=10.0,
        config=None
    ):
        super().__init__(name, config)
        self.channel = channel
        self.sample_rate = sample_rate
        self.samples_per_channel = samples_per_channel
        self.min_val = min_val
        self.max_val = max_val
        self.task = None

    def initialize(self) -> None:
        """
        Initialize the NI DAQ task and configure the analog input channel.

        This method checks that the device specified in the channel exists among
        the available NI devices. If the device is not found, it raises an AssertionError
        and prints the available devices.

        Raises
        ------
        AssertionError
            If the device name extracted from the channel is not found among the available devices.
        """
        # Extract device name from the channel (e.g., "Dev1/ai0" => "Dev1")
        device_match = re.match(r"([^/]+)/", self.channel)
        assert device_match, f"Invalid channel format: {self.channel}"
        device_name = device_match.group(1)

        # Query the NI system for available devices
        ni_system = system.System.local()
        available_devices = [dev.name for dev in ni_system.devices]

        # Assertion to ensure the device exists
        assert device_name in available_devices, (
            f"Device '{device_name}' not found. Available devices: {', '.join(available_devices)}"
        )
        print(f"Device '{device_name}' found among available devices: {', '.join(available_devices)}")

        # Initialize and configure the NI DAQ task
        self.task = Task()
        self.task.ai_channels.add_ai_voltage_chan(
            self.channel, min_val=self.min_val, max_val=self.max_val
        )
        self.task.timing.cfg_samp_clk_timing(
            rate=self.sample_rate,
            sample_mode=AcquisitionType.CONTINUOUS,
            samps_per_chan=self.samples_per_channel
        )
        print(f"{self.name} initialized on channel {self.channel}")

    def read(self, number_of_samples: int = None) -> list:
        """
        Read data from the NI DAQ device.

        Parameters
        ----------
        number_of_samples : int, optional
            Number of samples to read. Defaults to self.samples_per_channel.

        Returns
        -------
        list
            List of acquired voltage values.

        Raises
        ------
        Exception
            If the device is not initialized.
        """
        if self.task is None:
            raise Exception("Device not initialized. Please call initialize() first.")

        number_of_samples = number_of_samples or self.samples_per_channel
        data = self.task.read(number_of_samples_per_channel=number_of_samples)
        return data

    def write(self, command):
        """
        Send a command to the instrument.

        Parameters
        ----------
        command : any
            The command or data to be written.

        Raises
        ------
        NotImplementedError
            Since write is not supported for NI DAQ analog input.
        """
        raise NotImplementedError("Write operation is not supported for NI DAQ analog input.")

    def shutdown(self) -> None:
        """
        Properly close the NI DAQ task.
        """
        if self.task is not None:
            self.task.close()
            self.task = None
        print(f"{self.name} shutdown.")
