---
sidebar_position: 2
title: روبوٹ کے اجزاء اور فن تعمیر
description: ہیومنائیڈ روبوٹس کو بنانے والے اہم ہارڈویئر اور سافٹ ویئر اجزاء کی تلاش کریں۔
---

# باب 2: روبوٹ کے اجزاء اور فن تعمیر

## سیکھنے کے مقاصد

اس باب کے اختتام تک، آپ یہ کر سکیں گے:

- ہیومنائیڈ روبوٹس کے اہم ہارڈویئر اجزاء کی شناخت کریں
- ہیومنائیڈ سسٹمز میں استعمال ہونے والے سافٹ ویئر فن تعمیر کو سمجھیں
- روبوٹ کی مجموعی فعالیت میں ہر جزو کے کردار کی وضاحت کریں
- ہیومنائیڈ روبوٹ ڈیزائن میں انضمام کے چیلنجز بیان کریں

## 2.1 ہیومنائیڈ فن تعمیر کا جائزہ

ہیومنائیڈ روبوٹ میکانی، برقی، اور سافٹ ویئر سسٹمز کا ایک پیچیدہ انضمام ہے۔ فن تعمیر کو سمجھنا ان سسٹمز کو ڈیزائن، پروگرام، اور برقرار رکھنے کے لیے ضروری ہے۔

> **کلیدی تصور:** ہیومنائیڈ روبوٹ فن تعمیر ایک درجہ بندی ڈیزائن کی پیروی کرتا ہے جہاں نچلی سطح کا ہارڈویئر درمیانی سطح کے کنٹرول سسٹمز سے منسلک ہوتا ہے، جو اعلیٰ سطح کی منصوبہ بندی اور AI ماڈیولز کے ذریعے مربوط ہوتے ہیں۔

### سسٹم فن تعمیر کی پرتیں

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

## 2.2 میکانی ساخت

### ڈھانچہ فریم ورک

میکانی ساخت جسمانی شکل اور بوجھ برداشت کرنے کی صلاحیت فراہم کرتی ہے:

| جزو | مواد | مقصد |
|-----|------|------|
| **فریم** | ایلومینیم الائے، کاربن فائبر | ساختی سپورٹ |
| **جوڑ** | سٹیل، ٹائٹینیم | آرٹیکولیشن پوائنٹس |
| **کورز** | ABS پلاسٹک، فائبر گلاس | تحفظ، ظاہری شکل |
| **اینڈ ایفیکٹرز** | مختلف کمپوزٹس | ماحول کے ساتھ تعامل |

### جوڑوں کے میکانزم

ہیومنائیڈ روبوٹس انسان جیسی حرکت حاصل کرنے کے لیے مختلف قسم کے جوڑ استعمال کرتے ہیں:

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

# مثال: کندھے کا جوڑ بیان کریں
shoulder_pitch = Joint(
    name="right_shoulder_pitch",
    joint_type=JointType.REVOLUTE,
    range_min=-180,
    range_max=60,
    max_torque=40.0,
    max_velocity=3.14  # ~180 deg/s
)
```

### وزن کی تقسیم

توازن کے لیے مناسب وزن کی تقسیم اہم ہے:

```python
class HumanoidWeightDistribution:
    """Analyze weight distribution for balance optimization."""

    def __init__(self):
        # عام وزن کی تقسیم (کل کا فیصد)
        self.distribution = {
            "head": 7,
            "torso": 35,
            "each_arm": 6,      # x2 = 12%
            "each_leg": 18,     # x2 = 36%
            "pelvis": 10,
        }

    def calculate_com_height(self, total_height: float) -> float:
        """
        مرکز کثافت کی اونچائی کا تخمینہ لگائیں۔
        ہیومنائیڈز کے لیے، COM عام طور پر کل اونچائی کے 55-60% پر ہوتا ہے۔
        """
        return total_height * 0.57

    def get_segment_weight(self, segment: str, total_weight: float) -> float:
        """Calculate weight of a specific segment."""
        percentage = self.distribution.get(segment, 0)
        return (percentage / 100) * total_weight

# 70kg ہیومنائیڈ روبوٹ کے لیے حساب
weight_calc = HumanoidWeightDistribution()
torso_weight = weight_calc.get_segment_weight("torso", 70)
print(f"دھڑ کا وزن: {torso_weight} kg")  # 24.5 kg
```

## 2.3 ایکچویشن سسٹمز

ایکچویٹرز ہیومنائیڈ روبوٹس کے "پٹھے" ہیں، توانائی کو حرکت میں تبدیل کرتے ہیں۔

### ایکچویٹرز کی اقسام

#### الیکٹرک موٹرز

جدید ہیومنائیڈز میں سب سے عام ایکچویٹر قسم:

| موٹر کی قسم | فوائد | نقصانات | استعمال |
|------------|-------|---------|--------|
| **DC Brushed** | سادہ، کم لاگت | برش کا ٹوٹنا | کم لاگت پروٹوٹائپس |
| **BLDC** | اعلیٰ کارکردگی، لمبی عمر | پیچیدہ کنٹرول | جوڑوں کی ایکچویشن |
| **Servo** | مربوط کنٹرول | محدود ٹارک | چھوٹے جوڑ، ہاتھ |
| **Stepper** | درست پوزیشننگ | کم رفتار | کیمرے، سینسرز |

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

# مثال: Maxon EC-i 40 موٹر
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

#### ہائیڈرولک ایکچویٹرز

Atlas جیسی اعلیٰ طاقت کی ایپلیکیشنز میں استعمال:

- **فوائد:** اعلیٰ طاقت سے وزن کا تناسب، ہموار حرکت
- **نقصانات:** پیچیدہ پائپنگ، ممکنہ رساو، شور

#### نیومیٹک ایکچویٹرز

سافٹ روبوٹکس اور گرپرز میں عام:

- **فوائد:** لچکدار، انسانی تعامل کے لیے محفوظ
- **نقصانات:** درست کنٹرول مشکل، ہوا کی سپلائی ضروری

### سیریز الاسٹک ایکچویٹرز (SEA)

جدید ہیومنائیڈز اکثر محفوظ انسانی تعامل کے لیے Series Elastic Actuators استعمال کرتے ہیں:

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

# مثال: SEA کے ساتھ ٹانگ ایکچویٹر
leg_sea = SeriesElasticActuator(motor_torque=100, spring_constant=500)
deflection = leg_sea.set_desired_torque(50)  # 50 Nm مطلوب
print(f"سپرنگ انحراف: {deflection:.3f} rad")
```

## 2.4 پاور سسٹمز

پاور مینجمنٹ ہیومنائیڈ آپریشن کے لیے اہم ہے۔

### بیٹری ٹیکنالوجیز

| ٹیکنالوجی | انرجی ڈینسٹی | سائیکل لائف | ہیومنائیڈز میں استعمال |
|-----------|--------------|------------|---------------------|
| **Li-ion** | 150-250 Wh/kg | 500-1000 | سب سے عام |
| **LiPo** | 180-250 Wh/kg | 300-500 | ہلکے وزن کی ایپلیکیشنز |
| **Li-Fe** | 90-120 Wh/kg | 2000+ | حفاظت اہم |
| **Solid-state** | 300+ Wh/kg | 1000+ | مستقبل کی ٹیکنالوجی |

### پاور بجٹ تجزیہ

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

# مثال: ہیومنائیڈ روبوٹ کے لیے پاور بجٹ
budget = PowerBudget(battery_capacity_wh=1000)  # 1 kWh بیٹری

budget.add_consumer("leg_motors", 200, duty_cycle=0.6)
budget.add_consumer("arm_motors", 80, duty_cycle=0.4)
budget.add_consumer("computing", 100, duty_cycle=1.0)
budget.add_consumer("sensors", 30, duty_cycle=1.0)

print(f"کل اوسط طاقت: {budget.total_average_power():.0f} W")
print(f"تخمینی رن ٹائم: {budget.estimated_runtime_hours():.1f} گھنٹے")
```

## 2.5 کمپیوٹنگ فن تعمیر

### آن بورڈ کمپیوٹنگ

جدید ہیومنائیڈز کو اہم کمپیوٹنگ طاقت درکار ہے:

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

# ہیومنائیڈز کے لیے عام کمپیوٹنگ پلیٹ فارمز
platforms = [
    ComputeUnit("NVIDIA Jetson AGX Orin", 12, 2.2, 275, 64, 60),
    ComputeUnit("Intel NUC 12 Pro", 14, 4.7, 0, 32, 28),
    ComputeUnit("Raspberry Pi 5", 4, 2.4, 0, 8, 5),
]

# پلیٹ فارمز کا موازنہ
for p in platforms:
    print(f"{p.name}: {p.gpu_tflops} TFLOPS, {p.power_watts}W")
```

### سافٹ ویئر فن تعمیر

ہیومنائیڈ روبوٹ سافٹ ویئر عام طور پر ماڈیولر فن تعمیر کی پیروی کرتا ہے:

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

### ROS 2 انضمام

Robot Operating System 2 (ROS 2) معیاری مڈل ویئر ہے:

```python
# مثال: سادہ ROS 2 جوائنٹ سٹیٹ پبلشر (تصوراتی)
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
            "header": {"stamp": "current_time", "frame_id": "base_link"},
            "name": self.joint_names,
            "position": self.positions,
            "velocity": self.velocities,
            "effort": self.efforts
        }

# استعمال
joint_publisher = JointStatePublisher([
    "hip_yaw_l", "hip_roll_l", "hip_pitch_l",
    "knee_l", "ankle_pitch_l", "ankle_roll_l"
])
```

## 2.6 کمیونیکیشن سسٹمز

### اندرونی کمیونیکیشن

| پروٹوکول | رفتار | استعمال |
|----------|-------|--------|
| **EtherCAT** | 100 Mbps | ریئل ٹائم موٹر کنٹرول |
| **CAN bus** | 1 Mbps | سینسر نیٹ ورکس |
| **SPI** | 50+ Mbps | IMU، انکوڈرز |
| **I2C** | 400 kbps | کم رفتار سینسرز |
| **USB** | 480 Mbps | کیمرے، پیری فیرلز |

### بیرونی کمیونیکیشن

- **WiFi 6:** اعلیٰ بینڈوڈتھ ڈیٹا ٹرانسفر
- **5G:** ریموٹ آپریشن اور کلاؤڈ کمپیوٹنگ
- **Bluetooth:** پیری فیرل ڈیوائسز
- **Ethernet:** ٹیتھرڈ ڈیویلپمنٹ اور اعلیٰ قابل اعتماد لنکس

## خلاصہ

ہیومنائیڈ روبوٹس کا فن تعمیر میکانی، برقی، اور سافٹ ویئر سسٹمز کو ایک مربوط کل میں ضم کرتا ہے۔ اہم اجزاء میں شامل ہیں:

- **میکانی ساخت:** ڈھانچہ فریم ورک، جوڑ، اور ایکچویٹرز
- **ایکچویشن سسٹمز:** الیکٹرک موٹرز، ہائیڈرولکس، اور SEAs
- **پاور سسٹمز:** بیٹریاں اور پاور مینجمنٹ
- **کمپیوٹنگ:** آن بورڈ پروسیسرز اور سافٹ ویئر فن تعمیر
- **کمیونیکیشن:** اندرونی اور بیرونی نیٹ ورکنگ

## مراجعہ کے سوالات

1. ہیومنائیڈ روبوٹ سافٹ ویئر فن تعمیر کی اہم پرتیں کیا ہیں؟
2. ہیومنائیڈ ایپلیکیشنز کے لیے الیکٹرک موٹرز اور ہائیڈرولک ایکچویٹرز کا موازنہ کریں۔
3. انسان-روبوٹ تعامل کے لیے Series Elastic Actuators کو کیوں ترجیح دی جاتی ہے؟
4. بیٹری سے چلنے والے ہیومنائیڈ کے رن ٹائم کا تعین کرنے والے عوامل کیا ہیں؟
5. ہیومنائیڈ روبوٹ ڈیویلپمنٹ میں ROS 2 کے کردار کی وضاحت کریں۔

## عملی مشق

درج ذیل ضروریات کے ساتھ ہیومنائیڈ روبوٹ کے لیے پاور بجٹ ڈیزائن کریں:
- کم از کم 2 گھنٹے رن ٹائم
- 1.5 km/h کی رفتار سے چلنا
- کبھی کبھار آبجیکٹ مینیپولیشن
- مسلسل سینسر اور کمپیوٹنگ آپریشن

ضروری کم از کم بیٹری کیپیسٹی کا حساب لگائیں۔
