# iPhone IMU Visualizer

A small tool that replays accelerometer and gyroscope data as a 3D phone model. Orientation (roll, pitch, yaw) is estimated with a complementary filter and rendered in real time with Pygame and OpenGL.

The visualizer was written for recordings from an iPhone IMU, and it can also replay windows from the [UCI HAR dataset](https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones).

## How it works

1. Each CSV row (one sample) is converted to tilt angles from the accelerometer (`atan2` of the gravity vector).
2. The gyroscope rates are integrated over `dt` and blended with the accelerometer angles using a complementary filter (`alpha = 0.98` gyro, `0.02` accelerometer).
3. The resulting angles are precomputed for the whole file, then played back frame by frame on a colored box shaped like a phone. Each face has its own color so you can see which way it is facing.

Yaw is gyro-only (no magnetometer), so it will drift over time. This is expected.

## Project structure

| File | Purpose |
|---|---|
| `3D_IPHONE_ORIENTATION.py` | The visualizer. Reads a CSV, computes orientation, opens the 3D window. |
| `prepare_data.py` | Converts UCI HAR `Inertial Signals` files into a single CSV the visualizer can read. |
| `har_sample.csv` | Sample data: UCI HAR subject 1, walking (6080 rows, 50 Hz, about 2 minutes). |

## Requirements

- Python 3.9+
- `pygame`, `PyOpenGL`, `numpy`

```bash
pip install pygame PyOpenGL numpy
```

(`PyOpenGL_accelerate` is optional and can be skipped if it fails to build.)

## Quick start

```bash
git clone https://github.com/alenell/iPhoneIMUVisualizer.git
cd iPhoneIMUVisualizer
python 3D_IPHONE_ORIENTATION.py
```

This plays the bundled `har_sample.csv`. Close the window to quit. The recording loops when it reaches the end.

## Using your own data

### Input format

A CSV with **no header** and one sample per row:

```
ax, ay, az, gx, gy, gz
```

- Accelerometer: any consistent unit (only the ratios matter for tilt).
- Gyroscope: **radians per second**. If your app exports degrees per second, convert with `math.radians` before integrating.

### Settings to edit

At the top of `3D_IPHONE_ORIENTATION.py`:

| Variable | Meaning |
|---|---|
| `file_sim` | Path to your CSV. |
| `dt` | Sample period in seconds, `1 / sample_rate_hz`. For 50 Hz, `dt = 0.02`. A wrong value makes playback and integration run too fast or slow. |
| `alpha` | Gyro weight in the filter (`0.98` default). Higher trusts the gyro more (smoother, more drift); lower trusts the accelerometer more (less drift, noisier). |

### Axis and sign conventions

Accelerometer sign conventions differ between devices, and the visualizer's defaults are for the iPhone (gravity reads negative on the axis pointing up):

```python
pitch_acc = math.atan2(ax, math.sqrt(ay**2 + az**2))
roll_acc  = math.atan2(-ay, -az)
```

For the UCI HAR data (gravity reads positive), use:

```python
pitch_acc = math.atan2(-ax, math.sqrt(ay**2 + az**2))
roll_acc  = math.atan2(ay, az)
```

If the model tilts the wrong way or looks mirrored, flip signs here first, then try swapping or negating the angles in the `glRotatef` calls.

## Using the UCI HAR dataset

1. Download and unzip the [UCI HAR dataset](https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones).
2. In `prepare_data.py`, set `root` to the dataset's `train` (or `test`) folder, and choose a subject and activity:

   ```python
   SUBJECT, ACTIVITY = 1, 1   # 1=walking, 2=upstairs, 3=downstairs, 4=sitting, 5=standing, 6=laying
   ```

3. Run it:

   ```bash
   python prepare_data.py
   ```

   This writes `har_sample.csv` to the current directory.

Notes on the conversion:

- It uses `total_acc_*` (gravity included, needed for tilt) and `body_gyro_*` (rad/s).
- HAR windows are 128 samples with 50% overlap, so the script keeps the first 64 samples of each window to rebuild a continuous signal. It assumes the selected windows are consecutive; gaps in the original recording show up as jumps in the motion.
- Walking gives the most interesting motion. Sitting and standing barely move.

## Troubleshooting

| Problem | Fix |
|---|---|
| Blank window | Make sure you are on the current version of the script (projection set in `GL_PROJECTION`, camera translation re-applied each frame, depth test enabled). |
| `FileNotFoundError` in `prepare_data.py` | Check that `root` points at the `train` folder and that it contains `Inertial Signals`. |
| `ModuleNotFoundError: OpenGL` | The package is `PyOpenGL`, not `opengl`. Install it into the same environment you run the script from. |
| Motion looks too fast or slow | Set `dt` to match your sensor's sample rate. |
| Model rotates in the wrong direction | See [Axis and sign conventions](#axis-and-sign-conventions). |
| Strange behavior near ±90° pitch | Euler angles suffer from gimbal lock. A quaternion filter (Madgwick or Mahony) would avoid this. |

## Limitations

- Yaw drifts, since there is no magnetometer correction.
- Euler-angle rendering is subject to gimbal lock at extreme pitch.
- Sample rate is fixed by `dt`; timestamps in the data are not used.

## Author

Alex Lenell
