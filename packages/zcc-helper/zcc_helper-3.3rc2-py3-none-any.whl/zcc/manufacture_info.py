"""ControlPointManufactureInfo Class."""

from dataclasses import dataclass


@dataclass
class ControlPointManufactureInfo:
    """Data class to store ControlPoint manufacture_info."""

    identifier: str = None
    manufacturer: str = None
    model: str = None
    hwVersion: str = None
    firmwareVersion: str = None

    def describe(self) -> str:
        """Returns a description of a device"""
        return "%-40s %-40.40s %-8.8s          %s\n" % (
            self.identifier,
            f"{self.model} ({self.manufacturer})",
            "device",
            f"( hw={self.hwVersion}, fw={self.firmwareVersion} )",
        )
