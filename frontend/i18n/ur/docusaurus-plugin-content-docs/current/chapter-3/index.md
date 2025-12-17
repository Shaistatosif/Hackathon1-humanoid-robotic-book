---
sidebar_position: 3
title: سینسرز اور ایکچویٹرز
description: سینسنگ اور ایکچویشن سسٹمز کا گہرائی سے جائزہ جو ہیومنائیڈ روبوٹ کے ادراک اور حرکت کو ممکن بناتے ہیں۔
---

# باب 3: سینسرز اور ایکچویٹرز

## سیکھنے کے مقاصد

اس باب کے اختتام تک، آپ یہ کر سکیں گے:

- ہیومنائیڈ روبوٹس میں استعمال ہونے والی اہم سینسر اقسام کی شناخت اور وضاحت کریں
- سینسر فیوژن اور روبوٹ ادراک میں اس کی اہمیت کو سمجھیں
- مختلف ایکچویٹر کنٹرول حکمت عملیوں کی وضاحت کریں
- بنیادی سینسر پروسیسنگ پائپ لائنز ڈیزائن کریں

## 3.1 روبوٹ سینسنگ کا تعارف

سینسرز ہیومنائیڈ روبوٹس کی "آنکھیں اور کان" ہیں، جو ماحول کو سمجھنے اور اس کے ساتھ تعامل کرنے کے لیے ضروری معلومات فراہم کرتے ہیں۔

> **کلیدی اصول:** مؤثر روبوٹ سینسنگ کے لیے متعدد تکمیلی سینسرز کی ضرورت ہوتی ہے جو سینسر فیوژن کے ذریعے مل کر کام کرتے ہیں تاکہ روبوٹ کی حالت اور ماحول کی قابل اعتماد سمجھ پیدا ہو۔

### سینسر کی اقسام

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class SensorCategory(Enum):
    """Categories of sensors in humanoid robots."""
    PROPRIOCEPTIVE = "proprioceptive"  # اندرونی حالت
    EXTEROCEPTIVE = "exteroceptive"    # بیرونی ماحول
    TACTILE = "tactile"                 # چھونے/رابطہ

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

## 3.2 پروپریوسیپٹو سینسرز

پروپریوسیپٹو سینسرز روبوٹ کی اندرونی حالت کی پیمائش کرتے ہیں۔

### جوائنٹ پوزیشن انکوڈرز

انکوڈرز جوڑوں کی زاویہ پوزیشن کی پیمائش کرتے ہیں:

| انکوڈر کی قسم | ریزولوشن | فوائد | نقصانات |
|--------------|----------|-------|---------|
| **Incremental** | 1000-10000 CPR | کم لاگت، سادہ | ہومنگ ضروری |
| **Absolute** | 12-19 bits | ہومنگ ضروری نہیں | زیادہ لاگت |
| **Magnetic** | 12-14 bits | مضبوط، کمپیکٹ | کم درستگی |
| **Optical** | 16-23 bits | اعلیٰ درستگی | دھول حساس |

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

    def zero(self):
        """Set current position as zero reference."""
        self._zero_offset = (self._count / self.counts_per_rev) * 360.0

# مثال: 17-bit absolute انکوڈر
encoder = RotaryEncoder(resolution_bits=17)
print(f"ریزولوشن: {encoder.resolution_deg:.6f} ڈگریز")
print(f"فی انقلاب شمار: {encoder.counts_per_rev}")
```

### انرشیل میژرمنٹ یونٹس (IMU)

IMUs سمت اور حرکت کے احساس کے لیے متعدد سینسرز کو ملاتے ہیں:

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

        # عام شور کی خصوصیات
        self.accel_noise = 0.003  # g/√Hz
        self.gyro_noise = 0.01   # deg/s/√Hz

        # بائیاس (وقت کے ساتھ ڈرفٹ)
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

### فورس/ٹارک سینسرز

تعامل کی قوتوں کی پیمائش کے لیے ضروری:

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

    def read_calibrated(self) -> dict:
        """Read calibrated force/torque values."""
        raw = [0.0] * 6  # حقیقی نفاذ میں ہارڈویئر سے پڑھا جائے گا

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
        raw = [0.0] * 6
        for i in range(6):
            self._bias[i] = sum(self._calibration_matrix[i][j] * raw[j]
                               for j in range(6))
```

## 3.3 ایکسٹیروسیپٹو سینسرز

ایکسٹیروسیپٹو سینسرز بیرونی ماحول کو محسوس کرتے ہیں۔

### ویژن سسٹمز

کیمرے ہیومنائیڈ ادراک کے لیے بنیادی سینسرز ہیں:

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
            baseline: کیمروں کے درمیان فاصلہ میٹرز میں
            focal_length: فوکل لمبائی پکسلز میں
            resolution: (width, height)
        """
        self.baseline = baseline
        self.focal_length = focal_length
        self.resolution = resolution

    def disparity_to_depth(self, disparity: float) -> float:
        """
        disparity (پکسل فرق) کو گہرائی میں تبدیل کریں۔

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

# مثال: RealSense D435 طرز کا کیمرا
stereo = StereoCamera(
    baseline=0.05,        # 50mm بیس لائن
    focal_length=380,     # پکسلز
    resolution=(1280, 720)
)

# disparity سے گہرائی کا حساب
disparity = 38  # پکسلز
depth = stereo.disparity_to_depth(disparity)
print(f"Disparity {disparity}px → گہرائی {depth:.2f}m")
```

### LiDAR (لائٹ ڈیٹیکشن اینڈ رینجنگ)

LiDAR درست 3D ماحولیاتی نقشہ سازی فراہم کرتا ہے:

```python
@dataclass
class LiDARSpec:
    """LiDAR sensor specifications."""
    range_max: float       # میٹرز
    range_min: float       # میٹرز
    angular_resolution: float  # ڈگریز
    scan_rate: float      # Hz
    channels: int         # لیزر بیمز کی تعداد
    field_of_view: tuple  # (horizontal, vertical) ڈگریز
    accuracy: float       # میٹرز

class LiDARProcessor:
    """Process LiDAR point cloud data."""

    def __init__(self, spec: LiDARSpec):
        self.spec = spec

    def filter_points(self, points: List[tuple],
                      min_range: float = None,
                      max_range: float = None) -> List[tuple]:
        """
        پوائنٹ کلاؤڈ کو رینج کے مطابق فلٹر کریں۔
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
        Voxel grid filter استعمال کرتے ہوئے پوائنٹ کلاؤڈ کو ڈاؤن سیمپل کریں۔
        """
        voxels = {}

        for x, y, z in points:
            vx = int(x / voxel_size)
            vy = int(y / voxel_size)
            vz = int(z / voxel_size)
            key = (vx, vy, vz)

            if key not in voxels:
                voxels[key] = (x, y, z)

        return list(voxels.values())
```

## 3.4 ٹیکٹائل سینسرز

ٹیکٹائل سینسرز روبوٹس کو جسمانی رابطہ "محسوس" کرنے کے قابل بناتے ہیں۔

### ٹیکٹائل سینسرز کی اقسام

| قسم | اصول | حساسیت | ایپلیکیشنز |
|-----|------|--------|------------|
| **Resistive** | دباؤ مزاحمت بدلتا ہے | درمیانی | گرپرز |
| **Capacitive** | کیپیسیٹنس میں تبدیلی | اعلیٰ | جلد کے سینسرز |
| **Piezoelectric** | دباؤ سے وولٹیج پیدا | بہت اعلیٰ | پھسلن کا پتہ |
| **Optical** | روشنی کی شدت میں تبدیلی | اعلیٰ | انگلیوں کی نوک |
| **Barometric** | چیمبرز میں ہوا کا دباؤ | درمیانی | سافٹ گرپرز |

```python
class TactileSensor:
    """Tactile sensor array for robot skin."""

    def __init__(self, rows: int, cols: int,
                 spatial_resolution: float = 0.004):
        """
        Args:
            rows: ٹیکسل کی قطاروں کی تعداد
            cols: ٹیکسل کے کالموں کی تعداد
            spatial_resolution: ٹیکسلز کے درمیان فاصلہ میٹرز میں
        """
        self.rows = rows
        self.cols = cols
        self.spatial_resolution = spatial_resolution
        self.pressure_range = (0, 100)  # kPa

        # ٹیکسل ارے کو شروع کریں
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
        پریشر میپس کا موازنہ کرکے ممکنہ پھسلن کا پتہ لگائیں۔
        """
        for i in range(self.rows):
            for j in range(self.cols):
                diff = abs(self.taxels[i][j] - previous_map[i][j])
                if diff > threshold:
                    return True
        return False

# مثال: انگلی کی نوک کا ٹیکٹائل سینسر
fingertip = TactileSensor(rows=8, cols=8, spatial_resolution=0.003)
print(f"کل ٹیکسلز: {fingertip.total_taxels}")
print(f"سینسنگ ایریا: {fingertip.sensing_area * 1e6:.1f} mm²")
```

## 3.5 سینسر فیوژن

سینسر فیوژن بہتر درستگی کے لیے متعدد سینسرز سے ڈیٹا کو ملاتا ہے۔

### کمپلیمینٹری فلٹر

سمت کے لیے accelerometer اور gyroscope کا سادہ فیوژن:

```python
import math

class ComplementaryFilter:
    """
    IMU سمت کے تخمینے کے لیے کمپلیمینٹری فلٹر۔
    gyroscope (تیز، ڈرفٹ) کو accelerometer (سست، شور والا) کے ساتھ ملاتا ہے۔
    """

    def __init__(self, alpha: float = 0.98):
        """
        Args:
            alpha: gyroscope کے لیے وزن (0-1)۔ زیادہ = gyro پر زیادہ اعتماد۔
        """
        self.alpha = alpha
        self.pitch = 0.0
        self.roll = 0.0

    def update(self, accel: tuple, gyro: tuple, dt: float) -> tuple:
        """
        سمت کا تخمینہ اپڈیٹ کریں۔

        Args:
            accel: (ax, ay, az) m/s² میں
            gyro: (gx, gy, gz) rad/s میں
            dt: سیکنڈز میں وقت کا قدم

        Returns:
            (pitch, roll) ریڈینز میں
        """
        ax, ay, az = accel
        gx, gy, gz = gyro

        # gyroscope کو انٹیگریٹ کریں
        gyro_pitch = self.pitch + gx * dt
        gyro_roll = self.roll + gy * dt

        # accelerometer سے زاویوں کا حساب
        accel_pitch = math.atan2(ay, math.sqrt(ax**2 + az**2))
        accel_roll = math.atan2(-ax, az)

        # کمپلیمینٹری فلٹر کے ساتھ فیوز کریں
        self.pitch = self.alpha * gyro_pitch + (1 - self.alpha) * accel_pitch
        self.roll = self.alpha * gyro_roll + (1 - self.alpha) * accel_roll

        return (self.pitch, self.roll)

# مثال استعمال
cf = ComplementaryFilter(alpha=0.98)
accel = (0.1, 0.05, 9.8)  # m/s²
gyro = (0.01, 0.02, 0.0)  # rad/s
pitch, roll = cf.update(accel, gyro, dt=0.001)
print(f"Pitch: {math.degrees(pitch):.2f}°, Roll: {math.degrees(roll):.2f}°")
```

### سادہ کالمین فلٹر

مزید پیچیدہ سٹیٹ ایسٹیمیشن کے لیے:

```python
class SimpleKalmanFilter:
    """
    سینسر فیوژن مظاہرے کے لیے سادہ 1D کالمین فلٹر۔
    """

    def __init__(self, process_noise: float, measurement_noise: float,
                 initial_estimate: float = 0, initial_uncertainty: float = 1):
        """
        Args:
            process_noise: پراسیس نوائز ویرینس (Q)
            measurement_noise: میژرمنٹ نوائز ویرینس (R)
            initial_estimate: ابتدائی سٹیٹ تخمینہ
            initial_uncertainty: ابتدائی تخمینہ غیر یقینیت (P)
        """
        self.Q = process_noise
        self.R = measurement_noise
        self.x = initial_estimate  # سٹیٹ تخمینہ
        self.P = initial_uncertainty  # تخمینہ غیر یقینیت

    def predict(self, control_input: float = 0):
        """پیشگوئی کا مرحلہ۔"""
        self.x = self.x + control_input
        self.P = self.P + self.Q

    def update(self, measurement: float) -> float:
        """
        نئی پیمائش کے ساتھ اپڈیٹ مرحلہ۔

        Returns:
            اپڈیٹ شدہ سٹیٹ تخمینہ
        """
        # کالمین گین
        K = self.P / (self.P + self.R)

        # پیمائش کے ساتھ تخمینہ اپڈیٹ کریں
        self.x = self.x + K * (measurement - self.x)

        # غیر یقینیت اپڈیٹ کریں
        self.P = (1 - K) * self.P

        return self.x

# مثال: دو پوزیشن سینسرز کو فیوز کرنا
kf = SimpleKalmanFilter(
    process_noise=0.1,
    measurement_noise=1.0,
    initial_estimate=0,
    initial_uncertainty=10
)

# پیمائشوں کی نقل
measurements = [1.2, 0.9, 1.1, 1.0, 0.8, 1.1, 1.0]
for m in measurements:
    kf.predict()
    estimate = kf.update(m)
    print(f"پیمائش: {m:.2f}, تخمینہ: {estimate:.2f}, غیر یقینیت: {kf.P:.3f}")
```

## 3.6 ایکچویٹر کنٹرول

مؤثر ایکچویٹر کنٹرول ہموار، درست حرکت کے لیے ضروری ہے۔

### PID کنٹرول

سب سے عام کنٹرول حکمت عملی:

```python
class PIDController:
    """PID controller for actuator position/velocity control."""

    def __init__(self, kp: float, ki: float, kd: float,
                 output_limits: tuple = (-float('inf'), float('inf'))):
        """
        Args:
            kp: تناسبی گین
            ki: انٹیگرل گین
            kd: ڈیریویٹو گین
            output_limits: (min, max) آؤٹ پٹ حدود
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min, self.output_max = output_limits

        self.integral = 0
        self.previous_error = 0

    def reset(self):
        """Reset controller state."""
        self.integral = 0
        self.previous_error = 0

    def compute(self, setpoint: float, measured: float,
                dt: float) -> float:
        """
        کنٹرول آؤٹ پٹ کا حساب لگائیں۔

        Args:
            setpoint: مطلوبہ قدر
            measured: موجودہ پیمائش شدہ قدر
            dt: سیکنڈز میں وقت کا قدم

        Returns:
            کنٹرول آؤٹ پٹ
        """
        error = setpoint - measured

        # تناسبی ٹرم
        p_term = self.kp * error

        # انٹیگرل ٹرم (anti-windup کے ساتھ)
        self.integral += error * dt
        i_term = self.ki * self.integral

        # ڈیریویٹو ٹرم
        if dt > 0:
            derivative = (error - self.previous_error) / dt
        else:
            derivative = 0
        d_term = self.kd * derivative

        # آؤٹ پٹ کا حساب
        output = p_term + i_term + d_term

        # آؤٹ پٹ حدود لاگو کریں
        output = max(self.output_min, min(self.output_max, output))

        self.previous_error = error

        return output

# مثال: جوائنٹ پوزیشن کنٹرولر
joint_controller = PIDController(
    kp=100,      # پوزیشن گین
    ki=10,       # انٹیگرل گین
    kd=20,       # ڈیریویٹو گین
    output_limits=(-50, 50)  # Nm میں ٹارک حدود
)

# کنٹرول لوپ کی نقل
setpoint = 1.0  # ریڈینز میں ہدف پوزیشن
current_position = 0.0
dt = 0.001  # 1 kHz کنٹرول ریٹ

for i in range(100):
    torque = joint_controller.compute(setpoint, current_position, dt)
    # سادہ ڈائنامکس سمولیشن
    acceleration = torque / 1.0
    current_position += acceleration * dt * dt

    if i % 20 == 0:
        print(f"قدم {i}: پوزیشن={current_position:.3f}, ٹارک={torque:.2f}")
```

## خلاصہ

سینسرز اور ایکچویٹرز جسمانی دنیا کے ساتھ ہیومنائیڈ روبوٹ تعامل کی بنیاد ہیں:

- **پروپریوسیپٹو سینسرز** (انکوڈرز، IMUs، F/T سینسرز) اندرونی حالت کی پیمائش کرتے ہیں
- **ایکسٹیروسیپٹو سینسرز** (کیمرے، LiDAR) ماحول کو محسوس کرتے ہیں
- **ٹیکٹائل سینسرز** چھونے کا احساس اور مینیپولیشن ممکن بناتے ہیں
- **سینسر فیوژن** مضبوط تخمینے کے لیے متعدد سینسرز کو ملاتا ہے
- **کنٹرول الگورتھمز** (PID، ماڈل پر مبنی) درست ایکچویٹر رویے کو یقینی بناتے ہیں

## مراجعہ کے سوالات

1. پروپریوسیپٹو اور ایکسٹیروسیپٹو سینسرز میں کیا فرق ہے؟
2. ہیومنائیڈ روبوٹس میں سینسر فیوژن کیوں ضروری ہے؟
3. سٹیریو کیمرا disparity سے گہرائی کا حساب کیسے لگاتا ہے؟
4. PID کنٹرولر میں تین ٹرمز اور ان کے مقاصد کیا ہیں؟
5. ٹیکٹائل سینسر ارے پھسلن کا پتہ کیسے لگاتا ہے؟

## عملی مشق

ایک کمپلیمینٹری فلٹر نافذ کریں جو:
- pitch/roll کے لیے Accelerometer ڈیٹا
- تبدیلی کی شرح کے لیے Gyroscope ڈیٹا
- yaw کے لیے Magnetometer ڈیٹا

کو فیوز کرے۔ نقلی سینسر ڈیٹا کے ساتھ اپنے نفاذ کی جانچ کریں اور مختلف alpha اقدار کا موازنہ کریں۔
