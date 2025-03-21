from nidaqmx import system

class DeviceManager:
    """
    A flexible manager for querying and displaying available NI devices.
    """

    def __init__(self):
        self.devices = []
        self.refresh()

    def refresh(self):
        """
        Refresh the list of available NI devices.
        """
        ni_sys = system.System.local()
        self.devices = [device.name for device in ni_sys.devices]

    def list_devices(self):
        """
        Get the list of available NI devices.
        """
        return self.devices

    def print_devices(self):
        """
        Print out the available NI devices in a formatted manner.
        """
        if not self.devices:
            print("No NI devices found.")
        else:
            print("Available NI Devices:")
            for idx, device in enumerate(self.devices, start=1):
                print(f" {idx}. {device}")

    def get_device_by_name(self, name):
        """
        Retrieve a device name if it exists in the available devices list.
        """
        if name in self.devices:
            return name
        else:
            available = ", ".join(self.devices) if self.devices else "None"
            raise ValueError(f"Device '{name}' not found. Available devices: {available}")

# Create a module-level singleton instance.
device_manager = DeviceManager()