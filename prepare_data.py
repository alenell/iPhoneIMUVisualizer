import os
import numpy as np

root = "Path to UCI HAR training folder"
sig = os.path.join(root, "Inertial Signals")

def load(name):
    return np.loadtxt(os.path.join(sig, f"{name}_train.txt"))   # shape (n_windows, 128)

ax, ay, az = (load(f"total_acc_{c}") for c in "xyz")
gx, gy, gz = (load(f"body_gyro_{c}") for c in "xyz")

labels = np.loadtxt(os.path.join(root, "y_train.txt"), dtype=int)
subjects = np.loadtxt(os.path.join(root, "subject_train.txt"), dtype=int)

SUBJECT, ACTIVITY = 1, 1   # subject 1, walking

idx = np.where((subjects == SUBJECT) & (labels == ACTIVITY))[0]

def stitch(a):
    # first half of each window, to undo the 50% overlap
    return a[idx, :64].reshape(-1)

data = np.column_stack([stitch(a) for a in (ax, ay, az, gx, gy, gz)])
np.savetxt("har_sample.csv", data, delimiter=",")
print(data.shape)