---
sidebar_position: 2
title: Robot Components and Architecture
description: Explore the key hardware and software components that make up humanoid robots.
---

# Chapter 2: Robot Components and Architecture

## Learning Objectives

By the end of this chapter, you will be able to:

- Identify the major hardware components of humanoid robots
- Understand the software architecture used in humanoid systems
- Explain the role of each component in overall robot functionality
- Describe the integration challenges in humanoid robot design

## 2.1 Overview of Humanoid Architecture

A humanoid robot is a complex integration of mechanical, electrical, and software systems. Understanding the architecture is essential for designing, programming, and maintaining these systems.

> **Key Concept:** Humanoid robot architecture follows a hierarchical design where low-level hardware interfaces with mid-level control systems, which are coordinated by high-level planning and AI modules.

### System Architecture Layers

```
┌─────────────────────────────────────────────┐
│           High-Level Planning               │
│    (AI, Task Planning, Decision Making)     │
├─────────────────────────────────────────────┤
│          Mid-Level Control                  │
│   (Motion Planning, Trajectory Generation)  │
├─────────────────────────────────────────────┤
│          Low-Level Control                  │
│    (Motor Control, Sensor Processing)       │
├─────────────────────────────────────────────┤
│             Hardware Layer                  │
│  (Actuators, Sensors, Power, Structure)     │
└─────────────────────────────────────────────┘
```

## 2.2 Mechanical Structure

### Skeletal Framework

The mechanical structure provides the physical form and load-bearing capability:

| Component | Material | Purpose |
|-----------|----------|---------|
| **Frame** | Aluminum alloy, Carbon fiber | Structural support |
| **Joints** | Steel, Titanium | Articulation points |
| **Covers** | ABS plastic, Fiberglass | Protection, aesthetics |
| **End effectors** | Various composites | Interaction with environment |

### Joint Mechanisms

Humanoid robots employ various joint types to achieve human-like movement:

```python
from enum import Enum
from dataclasses import dataclass

class JointType(Enum):
    """Types of joints used in humanoid robots."""
    REVOLUTE = "revolute"      # Rotation around single axis
    PRISMATIC = "prismatic"    # Linear sliding motion
    SPHERICAL = "spherical"    # Ball-and-socket (3 DOF)
    UNIVERSAL = "universal"    # Two perpendicular axes (2 DOF)
    PLANAR = "planar"          # Motion in a plane (3 DOF)

@dataclass
class Joint:
    """Represents a robot joint."""
    name: str
    joint_type: JointType
    range_min: float  # degrees or mm
    range_max: float
    max_torque: float  # Nm
    max_velocity: float  # rad/s or mm/s

    def is_within_limits(self, position: float) -> bool:
        """Check if position is within joint limits."""
        return self.range_min <= position <= self.range_max

# Example: Define shoulder joint
shoulder_pitch = Joint(
    name="right_shoulder_pitch",
    joint_type=JointType.REVOLUTE,
    range_min=-180,
    range_max=60,
    max_torque=40.0,
    max_velocity=3.14  # ~180 deg/s
)
```

### Weight Distribution

Proper weight distribution is critical for balance:

```python
class HumanoidWeightDistribution:
    """Analyze weight distribution for balance optimization."""

    def __init__(self):
        # Typical weight distribution (percentage of total)
        self.distribution = {
            "head": 7,
            "torso": 35,
            "each_arm": 6,      # x2 = 12%
            "each_leg": 18,     # x2 = 36%
            "pelvis": 10,
        }

    def calculate_com_height(self, total_height: float) -> float:
        """
        Estimate center of mass height.
        For humanoids, COM is typically at 55-60% of total height.
        """
        return total_height * 0.57

    def get_segment_weight(self, segment: str, total_weight: float) -> float:
        """Calculate weight of a specific segment."""
        percentage = self.distribution.get(segment, 0)
        return (percentage / 100) * total_weight

# Calculate for a 70kg humanoid robot
weight_calc = HumanoidWeightDistribution()
torso_weight = weight_calc.get_segment_weight("torso", 70)
print(f"Torso weight: {torso_weight} kg")  # 24.5 kg
```

## 2.3 Actuation Systems

Actuators are the "muscles" of humanoid robots, converting energy into motion.

### Types of Actuators

#### Electric Motors

The most common actuator type in modern humanoids:

| Motor Type | Advantages | Disadvantages | Use Case |
|------------|------------|---------------|----------|
| **DC Brushed** | Simple, low cost | Brush wear, EMI | Low-cost prototypes |
| **BLDC** | High efficiency, long life | Complex control | Joint actuation |
| **Servo** | Integrated control | Limited torque | Small joints, hands |
| **Stepper** | Precise positioning | Low speed, vibration | Cameras, sensors |

```python
@dataclass
class ElectricMotor:
    """Specifications for an electric motor actuator."""
    model: str
    nominal_voltage: float      # V
    no_load_speed: float        # RPM
    stall_torque: float         # Nm
    continuous_torque: float    # Nm
    efficiency: float           # percentage
    weight: float               # kg

    def power_consumption(self, torque: float, speed: float) -> float:
        """Calculate power consumption at given operating point."""
        # P = τ * ω (torque * angular velocity)
        angular_velocity = (speed * 2 * 3.14159) / 60  # Convert RPM to rad/s
        mechanical_power = torque * angular_velocity
        return mechanical_power / (self.efficiency / 100)

# Example: Maxon EC-i 40 motor
motor = ElectricMotor(
    model="EC-i 40",
    nominal_voltage=24,
    no_load_speed=8000,
    stall_torque=0.5,
    continuous_torque=0.12,
    efficiency=89,
    weight=0.29
)
```

#### Hydraulic Actuators

Used in high-power applications like Atlas:

- **Advantages:** High power-to-weight ratio, smooth motion
- **Disadvantages:** Complex plumbing, potential leaks, noise

#### Pneumatic Actuators

Common in soft robotics and grippers:

- **Advantages:** Compliant, safe for human interaction
- **Disadvantages:** Difficult to control precisely, requires air supply

### Series Elastic Actuators (SEA)

Modern humanoids often use Series Elastic Actuators for safer human interaction:

```python
class SeriesElasticActuator:
    """
    Series Elastic Actuator with spring between motor and load.
    Provides compliance and force sensing.
    """

    def __init__(self, motor_torque: float, spring_constant: float):
        self.motor_torque = motor_torque  # Nm
        self.spring_constant = spring_constant  # Nm/rad
        self.spring_deflection = 0.0

    def get_output_torque(self) -> float:
        """Output torque is proportional to spring deflection."""
        return self.spring_constant * self.spring_deflection

    def set_desired_torque(self, desired_torque: float) -> float:
        """
        Control motor to achieve desired output torque.
        Returns required spring deflection.
        """
        required_deflection = desired_torque / self.spring_constant
        self.spring_deflection = required_deflection
        return required_deflection

    def impact_absorption(self, impact_energy: float) -> float:
        """
        Calculate spring deflection from impact.
        Energy = 0.5 * k * θ²
        """
        import math
        deflection = math.sqrt(2 * impact_energy / self.spring_constant)
        return deflection

# Example: Leg actuator with SEA
leg_sea = SeriesElasticActuator(motor_torque=100, spring_constant=500)
deflection = leg_sea.set_desired_torque(50)  # 50 Nm desired
print(f"Spring deflection: {deflection:.3f} rad ({deflection * 57.3:.1f} deg)")
```

## 2.4 Power Systems

Power management is critical for humanoid operation.

### Battery Technologies

| Technology | Energy Density | Cycle Life | Use in Humanoids |
|------------|---------------|------------|------------------|
| **Li-ion** | 150-250 Wh/kg | 500-1000 | Most common |
| **LiPo** | 180-250 Wh/kg | 300-500 | Lightweight applications |
| **Li-Fe** | 90-120 Wh/kg | 2000+ | Safety-critical |
| **Solid-state** | 300+ Wh/kg | 1000+ | Future technology |

### Power Budget Analysis

```python
class PowerBudget:
    """Analyze power consumption for humanoid robot systems."""

    def __init__(self, battery_capacity_wh: float):
        self.battery_capacity = battery_capacity_wh
        self.consumers = {}

    def add_consumer(self, name: str, power_watts: float, duty_cycle: float = 1.0):
        """Add a power consumer with optional duty cycle."""
        self.consumers[name] = {
            "power": power_watts,
            "duty_cycle": duty_cycle,
            "average_power": power_watts * duty_cycle
        }

    def total_average_power(self) -> float:
        """Calculate total average power consumption."""
        return sum(c["average_power"] for c in self.consumers.values())

    def estimated_runtime_hours(self) -> float:
        """Estimate battery runtime in hours."""
        total_power = self.total_average_power()
        if total_power == 0:
            return float('inf')
        return self.battery_capacity / total_power

    def power_breakdown(self) -> dict:
        """Get percentage breakdown of power consumption."""
        total = self.total_average_power()
        return {
            name: (c["average_power"] / total) * 100
            for name, c in self.consumers.items()
        }

# Example power budget for a humanoid robot
budget = PowerBudget(battery_capacity_wh=1000)  # 1 kWh battery

budget.add_consumer("leg_motors", 200, duty_cycle=0.6)
budget.add_consumer("arm_motors", 80, duty_cycle=0.4)
budget.add_consumer("hand_motors", 20, duty_cycle=0.3)
budget.add_consumer("computing", 100, duty_cycle=1.0)
budget.add_consumer("sensors", 30, duty_cycle=1.0)
budget.add_consumer("cooling", 50, duty_cycle=0.5)

print(f"Total average power: {budget.total_average_power():.0f} W")
print(f"Estimated runtime: {budget.estimated_runtime_hours():.1f} hours")
print(f"Power breakdown: {budget.power_breakdown()}")
```

## 2.5 Computing Architecture

### Onboard Computing

Modern humanoids require significant computing power:

```python
@dataclass
class ComputeUnit:
    """Computing unit specifications."""
    name: str
    cpu_cores: int
    cpu_freq_ghz: float
    gpu_tflops: float
    ram_gb: int
    power_watts: float

    def performance_per_watt(self) -> float:
        """Calculate TFLOPS per watt."""
        return self.gpu_tflops / self.power_watts

# Common computing platforms for humanoids
platforms = [
    ComputeUnit("NVIDIA Jetson AGX Orin", 12, 2.2, 275, 64, 60),
    ComputeUnit("Intel NUC 12 Pro", 14, 4.7, 0, 32, 28),
    ComputeUnit("Raspberry Pi 5", 4, 2.4, 0, 8, 5),
]

# Compare platforms
for p in platforms:
    print(f"{p.name}: {p.gpu_tflops} TFLOPS, {p.power_watts}W")
```

### Software Architecture

Humanoid robot software typically follows a modular architecture:

```
┌────────────────────────────────────────────────────────┐
│                    Application Layer                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Task     │  │ Human    │  │ Learning │             │
│  │ Planning │  │ Interface│  │ Modules  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
├────────────────────────────────────────────────────────┤
│                    Middleware Layer                     │
│  ┌──────────────────────────────────────────┐         │
│  │         ROS 2 (Robot Operating System)    │         │
│  └──────────────────────────────────────────┘         │
├────────────────────────────────────────────────────────┤
│                    Control Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Motion   │  │ Balance  │  │ Grasping │             │
│  │ Control  │  │ Control  │  │ Control  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
├────────────────────────────────────────────────────────┤
│                    Hardware Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Motor    │  │ Sensor   │  │ Comm     │             │
│  │ Drivers  │  │ Drivers  │  │ Drivers  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└────────────────────────────────────────────────────────┘
```

### ROS 2 Integration

Robot Operating System 2 (ROS 2) is the standard middleware:

```python
# Example: Simple ROS 2 joint state publisher (conceptual)
"""
ROS 2 node structure for humanoid joint control.
Note: This is a simplified example for educational purposes.
"""

class JointStatePublisher:
    """Publishes joint states at regular intervals."""

    def __init__(self, joint_names: list, publish_rate: float = 100):
        self.joint_names = joint_names
        self.publish_rate = publish_rate  # Hz
        self.positions = [0.0] * len(joint_names)
        self.velocities = [0.0] * len(joint_names)
        self.efforts = [0.0] * len(joint_names)

    def update_joint(self, index: int, position: float,
                     velocity: float = 0.0, effort: float = 0.0):
        """Update a single joint's state."""
        self.positions[index] = position
        self.velocities[index] = velocity
        self.efforts[index] = effort

    def get_message(self) -> dict:
        """Create joint state message."""
        return {
            "header": {
                "stamp": "current_time",
                "frame_id": "base_link"
            },
            "name": self.joint_names,
            "position": self.positions,
            "velocity": self.velocities,
            "effort": self.efforts
        }

# Usage
joint_publisher = JointStatePublisher([
    "hip_yaw_l", "hip_roll_l", "hip_pitch_l",
    "knee_l", "ankle_pitch_l", "ankle_roll_l"
])
```

## 2.6 Communication Systems

### Internal Communication

| Protocol | Speed | Use Case |
|----------|-------|----------|
| **EtherCAT** | 100 Mbps | Real-time motor control |
| **CAN bus** | 1 Mbps | Sensor networks |
| **SPI** | 50+ Mbps | IMU, encoders |
| **I2C** | 400 kbps | Low-speed sensors |
| **USB** | 480 Mbps | Cameras, peripherals |

### External Communication

- **WiFi 6:** High-bandwidth data transfer
- **5G:** Remote operation and cloud computing
- **Bluetooth:** Peripheral devices
- **Ethernet:** Tethered development and high-reliability links

## Summary

The architecture of humanoid robots integrates mechanical, electrical, and software systems into a cohesive whole. Key components include:

- **Mechanical structure:** Skeletal framework, joints, and actuators
- **Actuation systems:** Electric motors, hydraulics, and SEAs
- **Power systems:** Batteries and power management
- **Computing:** Onboard processors and software architecture
- **Communication:** Internal and external networking

Understanding these components is essential for designing, programming, and maintaining humanoid robot systems.

## Review Questions

1. What are the main layers in humanoid robot software architecture?
2. Compare electric motors and hydraulic actuators for humanoid applications.
3. Why are Series Elastic Actuators preferred for human-robot interaction?
4. What factors determine the runtime of a battery-powered humanoid?
5. Explain the role of ROS 2 in humanoid robot development.

## Hands-On Exercise

Design a power budget for a humanoid robot with the following requirements:
- 2-hour minimum runtime
- Walking at 1.5 km/h
- Occasional object manipulation
- Continuous sensor and computing operation

Calculate the minimum battery capacity needed.
