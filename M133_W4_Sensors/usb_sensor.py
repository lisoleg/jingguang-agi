# -*- coding: utf-8 -*-
"""
M133_W4_Sensors/usb_sensor.py
USB Sensor Interface (Simulated)
Part of M133: Cold-Start Bootstrap Experiment

Provides simulated USB sensor readings for the cold-start
bootstrap experiment. In a real deployment, these would
read from actual USB-attached sensors.

Supported sensor types:
- pendulum: period, length, amplitude
- counter: discrete counting observations
- ratio: ratio/comparison measurements
- continuity: continuity/density observations
- symmetry: symmetry/group observations
- force: force/acceleration measurements
- social: social norm observations
- cosmic: cosmological measurements
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SensorReading:
    """A single reading from a USB sensor."""
    sensor_type: str
    timestamp: float
    data: Dict[str, Any]
    raw_bytes: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "sensor_type": self.sensor_type,
            "timestamp": self.timestamp,
            "data": self.data,
            "raw_bytes": self.raw_bytes[:10],  # truncate for display
        }


class USBSensorInterface:
    """Simulated USB sensor interface.

    In production, this would communicate with real USB sensors
    via pyusb or serial. Here we simulate realistic sensor
    readings with appropriate noise models.
    """

    # Vendor/Product IDs for real sensors (for documentation)
    SENSOR_IDS = {
        "pendulum":   (0x1234, 0x0001),
        "counter":    (0x1234, 0x0002),
        "ratio":      (0x1234, 0x0003),
        "continuity": (0x1234, 0x0004),
        "symmetry":   (0x1234, 0x0005),
        "force":      (0x1234, 0x0006),
        "social":     (0x1234, 0x0007),
        "cosmic":     (0x1234, 0x0008),
    }

    def __init__(self, seed: Optional[int] = None) -> None:
        """Initialize the USB sensor interface.

        Args:
            seed: Random seed for reproducibility.
        """
        self.connected: bool = False
        self.read_count: int = 0
        if seed is not None:
            random.seed(seed)

    def connect(self) -> bool:
        """Simulate USB connection. Returns True on success."""
        self.connected = True
        print("[USBSensor] Connected to simulated sensor bus.")
        return True

    def disconnect(self) -> None:
        """Disconnect from USB sensor bus."""
        self.connected = False
        print("[USBSensor] Disconnected.")

    def _check_connected(self) -> None:
        """Raise if not connected."""
        if not self.connected:
            raise RuntimeError("USB sensor not connected. Call connect() first.")

    def read_pendulum(self) -> SensorReading:
        """Read pendulum sensor: period, length, amplitude."""
        self._check_connected()
        self.read_count += 1

        base_period = 2.006  # T = 2*pi*sqrt(L/g), L=1m
        data = {
            "period_s": round(base_period + random.gauss(0, 0.03), 4),
            "length_m": round(1.0 + random.gauss(0, 0.005), 4),
            "amplitude_rad": round(0.3 + random.gauss(0, 0.02), 4),
            "g_estimate": round(9.81 + random.gauss(0, 0.1), 4),
        }
        raw = [random.randint(0, 255) for _ in range(16)]
        return SensorReading(
            sensor_type="pendulum",
            timestamp=time.time(),
            data=data,
            raw_bytes=raw,
        )

    def read_counter(self) -> SensorReading:
        """Read counting sensor: discrete count observations."""
        self._check_connected()
        self.read_count += 1

        count = random.randint(3, 12)
        data = {
            "observations": list(range(1, count + 1)),
            "total_count": count,
            "max_observed": count,
        }
        raw = [random.randint(0, 255) for _ in range(8)]
        return SensorReading(
            sensor_type="counter",
            timestamp=time.time(),
            data=data,
            raw_bytes=raw,
        )

    def read_ratio(self) -> SensorReading:
        """Read ratio sensor: comparison measurements."""
        self._check_connected()
        self.read_count += 1

        measurements = [
            (random.randint(1, 10), random.randint(1, 10))
            for _ in range(5)
        ]
        data = {
            "numerator": measurements[0][0],
            "denominator": measurements[0][1],
            "measurements": measurements,
            "ratio_values": [
                round(n / max(d, 1), 4) for n, d in measurements
            ],
        }
        raw = [random.randint(0, 255) for _ in range(12)]
        return SensorReading(
            sensor_type="ratio",
            timestamp=time.time(),
            data=data,
            raw_bytes=raw,
        )

    def read_continuity(self) -> SensorReading:
        """Read continuity sensor: density observations."""
        self._check_connected()
        self.read_count += 1

        data = {
            "intervals": [
                (round(random.uniform(0, 1), 4), round(random.uniform(0, 1), 4))
                for _ in range(8)
            ],
            "convergent_sequence": [
                round(1.0 / (2 ** i), 6) for i in range(10)
            ],
            "density_observations": random.randint(50, 200),
        }
        raw = [random.randint(0, 255) for _ in range(20)]
        return SensorReading(
            sensor_type="continuity",
            timestamp=time.time(),
            data=data,
            raw_bytes=raw,
        )

    def read_symmetry(self) -> SensorReading:
        """Read symmetry sensor: group observations."""
        self._check_connected()
        self.read_count += 1

        data = {
            "rotations": [0, 90, 180, 270],
            "reflections": ["horizontal", "vertical", "diagonal"],
            "composition_table": [
                [0, 1, 2, 3],
                [1, 2, 3, 0],
                [2, 3, 0, 1],
                [3, 0, 1, 2],
            ],
            "order": 4,
        }
        raw = [random.randint(0, 255) for _ in range(16)]
        return SensorReading(
            sensor_type="symmetry",
            timestamp=time.time(),
            data=data,
            raw_bytes=raw,
        )

    def read_force(self) -> SensorReading:
        """Read force sensor: acceleration measurements."""
        self._check_connected()
        self.read_count += 1

        mass = round(1.0 + random.gauss(0, 0.05), 4)
        acc = round(9.81 + random.gauss(0, 0.3), 4)
        data = {
            "mass_kg": mass,
            "acceleration_ms2": acc,
            "force_N": round(mass * acc, 4),
            "energy_J": round(0.5 * mass * acc ** 2, 4),
        }
        raw = [random.randint(0, 255) for _ in range(12)]
        return SensorReading(
            sensor_type="force",
            timestamp=time.time(),
            data=data,
            raw_bytes=raw,
        )

    def read_social(self) -> SensorReading:
        """Read social sensor: norm compliance observations."""
        self._check_connected()
        self.read_count += 1

        data = {
            "norms_observed": ["cooperation", "fairness", "reciprocity"],
            "violations": random.randint(0, 2),
            "compliance_rate": round(0.75 + random.gauss(0, 0.08), 4),
            "obligation_pairs": [
                ("promise", "fulfill"),
                ("request", "acknowledge"),
                ("harm", "repair"),
            ],
        }
        raw = [random.randint(0, 255) for _ in range(8)]
        return SensorReading(
            sensor_type="social",
            timestamp=time.time(),
            data=data,
            raw_bytes=raw,
        )

    def read_cosmic(self) -> SensorReading:
        """Read cosmic sensor: large-scale observations."""
        self._check_connected()
        self.read_count += 1

        data = {
            "H0_estimate": round(67.4 + random.gauss(0, 1.5), 2),
            "CMB_temperature_K": round(2.725 + random.gauss(0, 0.0005), 4),
            "dark_energy_fraction": round(0.685 + random.gauss(0, 0.008), 4),
            "baryon_fraction": round(0.049 + random.gauss(0, 0.001), 4),
        }
        raw = [random.randint(0, 255) for _ in range(24)]
        return SensorReading(
            sensor_type="cosmic",
            timestamp=time.time(),
            data=data,
            raw_bytes=raw,
        )

    def read(self, sensor_type: str) -> SensorReading:
        """Generic read method by sensor type name.

        Args:
            sensor_type: One of the supported sensor types.

        Returns:
            SensorReading with the appropriate data.

        Raises:
            ValueError: If sensor_type is not recognized.
        """
        readers = {
            "pendulum": self.read_pendulum,
            "counter": self.read_counter,
            "ratio": self.read_ratio,
            "continuity": self.read_continuity,
            "symmetry": self.read_symmetry,
            "force": self.read_force,
            "social": self.read_social,
            "cosmic": self.read_cosmic,
        }
        if sensor_type not in readers:
            raise ValueError(
                f"Unknown sensor type: {sensor_type}. "
                f"Supported: {list(readers.keys())}"
            )
        return readers[sensor_type]()

    def read_all(self) -> List[SensorReading]:
        """Read from all sensor types.

        Returns:
            List of SensorReading, one per sensor type.
        """
        return [
            self.read_pendulum(),
            self.read_counter(),
            self.read_ratio(),
            self.read_continuity(),
            self.read_symmetry(),
            self.read_force(),
            self.read_social(),
            self.read_cosmic(),
        ]


# ============================================================
# Main (Self-test)
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("USB Sensor Interface - Self Test")
    print("=" * 60)

    sensor = USBSensorInterface(seed=42)
    sensor.connect()

    readings = sensor.read_all()
    for r in readings:
        print(f"\n[{r.sensor_type}] @ {r.timestamp:.3f}")
        for k, v in r.data.items():
            print(f"  {k}: {v}")

    print(f"\nTotal readings: {sensor.read_count}")
    sensor.disconnect()
    print("\nSelf-test complete.")
