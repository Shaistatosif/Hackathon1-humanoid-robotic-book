---
sidebar_position: 3
title: Sensors and Actuators
description: Deep dive into the sensing and actuation systems that enable humanoid robot perception and movement.
---

# Chapter 3: Sensors and Actuators

## Learning Objectives

By the end of this chapter, you will be able to:

- Identify and describe the main sensor types used in humanoid robots
- Understand sensor fusion and its importance in robot perception
- Explain different actuator control strategies
- Design basic sensor processing pipelines

## 3.1 Introduction to Robot Sensing

Sensors are the "eyes and ears" of humanoid robots, providing the information needed to perceive and interact with the environment.

> **Key Principle:** Effective robot sensing requires multiple complementary sensors working together through sensor fusion to create a reliable understanding of the robot's state and environment.

### Sensor Categories

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class SensorCategory(Enum):
    """Categories of sensors in humanoid robots."""
    PROPRIOCEPTIVE = "proprioceptive"  # Internal state
    EXTEROCEPTIVE = "exteroceptive"    # External environment
    TACTILE = "tactile"                 # Touch/contact

@dataclass
class Sensor:
    """Base class for robot sensors."""
    name: str
    category: SensorCategory
    sample_rate: float  # Hz
    resolution: float
    range_min: float
    range_max: float
    noise_std: float

    def is_reading_valid(self, value: float) -> bool:
        """Check if reading is within sensor range."""
        return self.range_min <= value <= self.range_max
```

## 3.2 Proprioceptive Sensors

Proprioceptive sensors measure the internal state of the robot.

### Joint Position Encoders

Encoders measure the angular position of joints:

| Encoder Type | Resolution | Advantages | Disadvantages |
|--------------|------------|------------|---------------|
| **Incremental** | 1000-10000 CPR | Low cost, simple | Requires homing |
| **Absolute** | 12-19 bits | No homing needed | Higher cost |
| **Magnetic** | 12-14 bits | Robust, compact | Lower precision |
| **Optical** | 16-23 bits | High precision | Dust sensitive |

```python
import math

class RotaryEncoder:
    """Simulates a rotary encoder for joint position sensing."""

    def __init__(self, resolution_bits: int, encoder_type: str = "absolute"):
        self.resolution_bits = resolution_bits
        self.counts_per_rev = 2 ** resolution_bits
        self.encoder_type = encoder_type
        self._count = 0
        self._zero_offset = 0

    @property
    def resolution_deg(self) -> float:
        """Resolution in degrees per count."""
        return 360.0 / self.counts_per_rev

    def read_position_deg(self) -> float:
        """Read current position in degrees."""
        raw_deg = (self._count / self.counts_per_rev) * 360.0
        return raw_deg - self._zero_offset

    def read_position_rad(self) -> float:
        """Read current position in radians."""
        return math.radians(self.read_position_deg())

    def set_count(self, count: int):
        """Simulate encoder count (for testing)."""
        self._count = count % self.counts_per_rev

    def zero(self):
        """Set current position as zero reference."""
        self._zero_offset = (self._count / self.counts_per_rev) * 360.0

# Example: 17-bit absolute encoder
encoder = RotaryEncoder(resolution_bits=17)
print(f"Resolution: {encoder.resolution_deg:.6f} degrees")
print(f"Counts per revolution: {encoder.counts_per_rev}")
```

### Inertial Measurement Units (IMU)

IMUs combine multiple sensors for orientation and motion sensing:

```python
@dataclass
class IMUReading:
    """Single IMU measurement."""
    accelerometer: tuple  # (ax, ay, az) in m/s²
    gyroscope: tuple      # (gx, gy, gz) in rad/s
    magnetometer: tuple   # (mx, my, mz) in μT (optional)
    timestamp: float      # seconds

class IMU:
    """Inertial Measurement Unit sensor."""

    def __init__(self, sample_rate: float = 1000):
        self.sample_rate = sample_rate
        self.accel_range = 16  # ±16g
        self.gyro_range = 2000  # ±2000 deg/s

        # Typical noise characteristics
        self.accel_noise = 0.003  # g/√Hz
        self.gyro_noise = 0.01   # deg/s/√Hz

        # Bias (drift over time)
        self.gyro_bias = [0.0, 0.0, 0.0]

    def calibrate_gyro_bias(self, samples: List[IMUReading]):
        """Calibrate gyroscope bias from stationary samples."""
        if not samples:
            return

        avg_gx = sum(s.gyroscope[0] for s in samples) / len(samples)
        avg_gy = sum(s.gyroscope[1] for s in samples) / len(samples)
        avg_gz = sum(s.gyroscope[2] for s in samples) / len(samples)

        self.gyro_bias = [avg_gx, avg_gy, avg_gz]

    def remove_bias(self, reading: IMUReading) -> IMUReading:
        """Remove calibrated bias from gyroscope readings."""
        corrected_gyro = (
            reading.gyroscope[0] - self.gyro_bias[0],
            reading.gyroscope[1] - self.gyro_bias[1],
            reading.gyroscope[2] - self.gyro_bias[2]
        )
        return IMUReading(
            accelerometer=reading.accelerometer,
            gyroscope=corrected_gyro,
            magnetometer=reading.magnetometer,
            timestamp=reading.timestamp
        )
```

### Force/Torque Sensors

Essential for measuring interaction forces:

```python
class ForceTorqueSensor:
    """6-axis force/torque sensor for wrist or ankle mounting."""

    def __init__(self, force_range: float = 500, torque_range: float = 50):
        """
        Args:
            force_range: Maximum force in Newtons (Fx, Fy, Fz)
            torque_range: Maximum torque in Nm (Tx, Ty, Tz)
        """
        self.force_range = force_range
        self.torque_range = torque_range
        self._calibration_matrix = self._identity_6x6()
        self._bias = [0.0] * 6

    def _identity_6x6(self):
        """Create 6x6 identity matrix."""
        return [[1 if i == j else 0 for j in range(6)] for i in range(6)]

    def read_raw(self) -> List[float]:
        """Read raw sensor values (simulated)."""
        # In real implementation, this would read from hardware
        return [0.0] * 6

    def read_calibrated(self) -> dict:
        """Read calibrated force/torque values."""
        raw = self.read_raw()

        # Apply calibration matrix and bias removal
        calibrated = []
        for i in range(6):
            value = sum(self._calibration_matrix[i][j] * raw[j]
                       for j in range(6))
            calibrated.append(value - self._bias[i])

        return {
            "force": {"x": calibrated[0], "y": calibrated[1], "z": calibrated[2]},
            "torque": {"x": calibrated[3], "y": calibrated[4], "z": calibrated[5]}
        }

    def tare(self):
        """Zero the sensor (remove current load as bias)."""
        raw = self.read_raw()
        for i in range(6):
            self._bias[i] = sum(self._calibration_matrix[i][j] * raw[j]
                               for j in range(6))
```

## 3.3 Exteroceptive Sensors

Exteroceptive sensors perceive the external environment.

### Vision Systems

Cameras are primary sensors for humanoid perception:

```python
@dataclass
class CameraSpec:
    """Camera sensor specifications."""
    resolution: tuple    # (width, height)
    frame_rate: float   # fps
    field_of_view: tuple  # (horizontal, vertical) degrees
    focal_length: float  # mm
    sensor_type: str    # "RGB", "Depth", "RGBD", "Stereo"

    @property
    def megapixels(self) -> float:
        """Calculate megapixels."""
        return (self.resolution[0] * self.resolution[1]) / 1_000_000

class StereoCamera:
    """Stereo camera system for depth perception."""

    def __init__(self, baseline: float, focal_length: float,
                 resolution: tuple):
        """
        Args:
            baseline: Distance between cameras in meters
            focal_length: Focal length in pixels
            resolution: (width, height)
        """
        self.baseline = baseline
        self.focal_length = focal_length
        self.resolution = resolution

    def disparity_to_depth(self, disparity: float) -> float:
        """
        Convert disparity (pixel difference) to depth.

        depth = (baseline * focal_length) / disparity
        """
        if disparity <= 0:
            return float('inf')
        return (self.baseline * self.focal_length) / disparity

    def depth_to_disparity(self, depth: float) -> float:
        """Convert depth to expected disparity."""
        if depth <= 0:
            return float('inf')
        return (self.baseline * self.focal_length) / depth

    def min_detectable_depth(self, max_disparity: int) -> float:
        """Minimum depth that can be detected."""
        return self.disparity_to_depth(max_disparity)

# Example: RealSense D435 style camera
stereo = StereoCamera(
    baseline=0.05,        # 50mm baseline
    focal_length=380,     # pixels
    resolution=(1280, 720)
)

# Calculate depth from disparity
disparity = 38  # pixels
depth = stereo.disparity_to_depth(disparity)
print(f"Disparity {disparity}px → Depth {depth:.2f}m")
```

### LiDAR (Light Detection and Ranging)

LiDAR provides precise 3D environmental mapping:

```python
@dataclass
class LiDARSpec:
    """LiDAR sensor specifications."""
    range_max: float       # meters
    range_min: float       # meters
    angular_resolution: float  # degrees
    scan_rate: float      # Hz
    channels: int         # number of laser beams
    field_of_view: tuple  # (horizontal, vertical) degrees
    accuracy: float       # meters

class LiDARProcessor:
    """Process LiDAR point cloud data."""

    def __init__(self, spec: LiDARSpec):
        self.spec = spec

    def filter_points(self, points: List[tuple],
                      min_range: float = None,
                      max_range: float = None) -> List[tuple]:
        """
        Filter point cloud by range.

        Args:
            points: List of (x, y, z) coordinates
            min_range: Minimum distance (default: sensor min)
            max_range: Maximum distance (default: sensor max)
        """
        min_r = min_range or self.spec.range_min
        max_r = max_range or self.spec.range_max

        filtered = []
        for x, y, z in points:
            distance = (x**2 + y**2 + z**2) ** 0.5
            if min_r <= distance <= max_r:
                filtered.append((x, y, z))

        return filtered

    def downsample_voxel(self, points: List[tuple],
                         voxel_size: float) -> List[tuple]:
        """
        Downsample point cloud using voxel grid filter.

        Args:
            points: List of (x, y, z) coordinates
            voxel_size: Size of voxel grid cells in meters
        """
        voxels = {}

        for x, y, z in points:
            # Calculate voxel index
            vx = int(x / voxel_size)
            vy = int(y / voxel_size)
            vz = int(z / voxel_size)
            key = (vx, vy, vz)

            # Keep first point in each voxel
            if key not in voxels:
                voxels[key] = (x, y, z)

        return list(voxels.values())
```

## 3.4 Tactile Sensors

Tactile sensors enable robots to "feel" physical contact.

### Types of Tactile Sensors

| Type | Principle | Sensitivity | Applications |
|------|-----------|-------------|--------------|
| **Resistive** | Pressure changes resistance | Medium | Grippers |
| **Capacitive** | Capacitance variation | High | Skin sensors |
| **Piezoelectric** | Generates voltage from pressure | Very high | Slip detection |
| **Optical** | Light intensity changes | High | Fingertips |
| **Barometric** | Air pressure in chambers | Medium | Soft grippers |

```python
class TactileSensor:
    """Tactile sensor array for robot skin."""

    def __init__(self, rows: int, cols: int,
                 spatial_resolution: float = 0.004):
        """
        Args:
            rows: Number of taxel rows
            cols: Number of taxel columns
            spatial_resolution: Distance between taxels in meters
        """
        self.rows = rows
        self.cols = cols
        self.spatial_resolution = spatial_resolution
        self.pressure_range = (0, 100)  # kPa

        # Initialize taxel array
        self.taxels = [[0.0 for _ in range(cols)] for _ in range(rows)]

    @property
    def total_taxels(self) -> int:
        """Total number of tactile elements."""
        return self.rows * self.cols

    @property
    def sensing_area(self) -> float:
        """Total sensing area in m²."""
        width = self.cols * self.spatial_resolution
        height = self.rows * self.spatial_resolution
        return width * height

    def read_pressure_map(self) -> List[List[float]]:
        """Read the full pressure map."""
        return [row[:] for row in self.taxels]

    def get_contact_centroid(self) -> Optional[tuple]:
        """Calculate centroid of contact area."""
        total_pressure = 0
        cx, cy = 0, 0

        for i, row in enumerate(self.taxels):
            for j, pressure in enumerate(row):
                if pressure > 0:
                    total_pressure += pressure
                    cx += j * pressure
                    cy += i * pressure

        if total_pressure == 0:
            return None

        return (cx / total_pressure, cy / total_pressure)

    def detect_slip(self, previous_map: List[List[float]],
                    threshold: float = 5.0) -> bool:
        """
        Detect potential slip by comparing pressure maps.

        Args:
            previous_map: Previous pressure reading
            threshold: Change threshold for slip detection
        """
        for i in range(self.rows):
            for j in range(self.cols):
                diff = abs(self.taxels[i][j] - previous_map[i][j])
                if diff > threshold:
                    return True
        return False

# Example: Fingertip tactile sensor
fingertip = TactileSensor(rows=8, cols=8, spatial_resolution=0.003)
print(f"Total taxels: {fingertip.total_taxels}")
print(f"Sensing area: {fingertip.sensing_area * 1e6:.1f} mm²")
```

## 3.5 Sensor Fusion

Sensor fusion combines data from multiple sensors for improved accuracy.

### Complementary Filter

Simple fusion of accelerometer and gyroscope for orientation:

```python
import math

class ComplementaryFilter:
    """
    Complementary filter for IMU orientation estimation.
    Combines gyroscope (fast, drifts) with accelerometer (slow, noisy).
    """

    def __init__(self, alpha: float = 0.98):
        """
        Args:
            alpha: Weight for gyroscope (0-1). Higher = trust gyro more.
        """
        self.alpha = alpha
        self.pitch = 0.0
        self.roll = 0.0

    def update(self, accel: tuple, gyro: tuple, dt: float) -> tuple:
        """
        Update orientation estimate.

        Args:
            accel: (ax, ay, az) in m/s²
            gyro: (gx, gy, gz) in rad/s
            dt: Time step in seconds

        Returns:
            (pitch, roll) in radians
        """
        ax, ay, az = accel
        gx, gy, gz = gyro

        # Integrate gyroscope
        gyro_pitch = self.pitch + gx * dt
        gyro_roll = self.roll + gy * dt

        # Calculate angles from accelerometer
        accel_pitch = math.atan2(ay, math.sqrt(ax**2 + az**2))
        accel_roll = math.atan2(-ax, az)

        # Fuse with complementary filter
        self.pitch = self.alpha * gyro_pitch + (1 - self.alpha) * accel_pitch
        self.roll = self.alpha * gyro_roll + (1 - self.alpha) * accel_roll

        return (self.pitch, self.roll)

# Example usage
cf = ComplementaryFilter(alpha=0.98)
accel = (0.1, 0.05, 9.8)  # m/s²
gyro = (0.01, 0.02, 0.0)  # rad/s
pitch, roll = cf.update(accel, gyro, dt=0.001)
print(f"Pitch: {math.degrees(pitch):.2f}°, Roll: {math.degrees(roll):.2f}°")
```

### Extended Kalman Filter

For more complex state estimation:

```python
class SimpleKalmanFilter:
    """
    Simplified 1D Kalman filter for sensor fusion demonstration.
    """

    def __init__(self, process_noise: float, measurement_noise: float,
                 initial_estimate: float = 0, initial_uncertainty: float = 1):
        """
        Args:
            process_noise: Process noise variance (Q)
            measurement_noise: Measurement noise variance (R)
            initial_estimate: Initial state estimate
            initial_uncertainty: Initial estimate uncertainty (P)
        """
        self.Q = process_noise
        self.R = measurement_noise
        self.x = initial_estimate  # State estimate
        self.P = initial_uncertainty  # Estimate uncertainty

    def predict(self, control_input: float = 0):
        """
        Prediction step.

        Args:
            control_input: Known control input affecting state
        """
        # State prediction (simple model: x_new = x + control)
        self.x = self.x + control_input

        # Uncertainty grows
        self.P = self.P + self.Q

    def update(self, measurement: float) -> float:
        """
        Update step with new measurement.

        Args:
            measurement: Sensor measurement

        Returns:
            Updated state estimate
        """
        # Kalman gain
        K = self.P / (self.P + self.R)

        # Update estimate with measurement
        self.x = self.x + K * (measurement - self.x)

        # Update uncertainty
        self.P = (1 - K) * self.P

        return self.x

# Example: Fusing two position sensors
kf = SimpleKalmanFilter(
    process_noise=0.1,
    measurement_noise=1.0,
    initial_estimate=0,
    initial_uncertainty=10
)

# Simulate measurements
measurements = [1.2, 0.9, 1.1, 1.0, 0.8, 1.1, 1.0]
for m in measurements:
    kf.predict()
    estimate = kf.update(m)
    print(f"Measurement: {m:.2f}, Estimate: {estimate:.2f}, "
          f"Uncertainty: {kf.P:.3f}")
```

## 3.6 Actuator Control

Effective actuator control is essential for smooth, precise movement.

### PID Control

The most common control strategy:

```python
class PIDController:
    """PID controller for actuator position/velocity control."""

    def __init__(self, kp: float, ki: float, kd: float,
                 output_limits: tuple = (-float('inf'), float('inf'))):
        """
        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            output_limits: (min, max) output limits
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min, self.output_max = output_limits

        self.integral = 0
        self.previous_error = 0
        self.previous_time = None

    def reset(self):
        """Reset controller state."""
        self.integral = 0
        self.previous_error = 0
        self.previous_time = None

    def compute(self, setpoint: float, measured: float,
                dt: float) -> float:
        """
        Compute control output.

        Args:
            setpoint: Desired value
            measured: Current measured value
            dt: Time step in seconds

        Returns:
            Control output
        """
        error = setpoint - measured

        # Proportional term
        p_term = self.kp * error

        # Integral term (with anti-windup)
        self.integral += error * dt
        i_term = self.ki * self.integral

        # Derivative term
        if dt > 0:
            derivative = (error - self.previous_error) / dt
        else:
            derivative = 0
        d_term = self.kd * derivative

        # Calculate output
        output = p_term + i_term + d_term

        # Apply output limits
        output = max(self.output_min, min(self.output_max, output))

        # Anti-windup: if output is saturated, don't accumulate integral
        if output == self.output_min or output == self.output_max:
            self.integral -= error * dt

        self.previous_error = error

        return output

# Example: Joint position controller
joint_controller = PIDController(
    kp=100,      # Position gain
    ki=10,       # Integral gain
    kd=20,       # Derivative gain
    output_limits=(-50, 50)  # Torque limits in Nm
)

# Simulate control loop
setpoint = 1.0  # Target position in radians
current_position = 0.0
dt = 0.001  # 1 kHz control rate

for i in range(100):
    torque = joint_controller.compute(setpoint, current_position, dt)
    # Simple dynamics simulation
    acceleration = torque / 1.0  # Assuming unit inertia
    current_position += acceleration * dt * dt

    if i % 20 == 0:
        print(f"Step {i}: Position={current_position:.3f}, Torque={torque:.2f}")
```

## Summary

Sensors and actuators are the foundation of humanoid robot interaction with the physical world:

- **Proprioceptive sensors** (encoders, IMUs, F/T sensors) measure internal state
- **Exteroceptive sensors** (cameras, LiDAR) perceive the environment
- **Tactile sensors** enable touch sensing and manipulation
- **Sensor fusion** combines multiple sensors for robust estimation
- **Control algorithms** (PID, model-based) ensure precise actuator behavior

## Review Questions

1. What is the difference between proprioceptive and exteroceptive sensors?
2. Why is sensor fusion necessary in humanoid robots?
3. Explain how a stereo camera calculates depth from disparity.
4. What are the three terms in a PID controller and their purposes?
5. How does a tactile sensor array detect slip?

## Hands-On Exercise

Implement a complementary filter that fuses:
- Accelerometer data for pitch/roll
- Gyroscope data for rate of change
- Magnetometer data for yaw

Test your implementation with simulated sensor data and compare different alpha values.
