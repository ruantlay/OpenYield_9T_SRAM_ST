import numpy as np
import matplotlib.pyplot as plt

# ===============================
# 1. Robust Xyce .prn parser
# ===============================
Vnoise = []
Q = []
QB = []

with open("DC_disturbance_curve.sp.prn", "r") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("*"):
            continue

        parts = line.split()

        # 只保留“全是数字”的行
        try:
            nums = [float(x) for x in parts]
        except ValueError:
            continue

        # 只取最后三列（Xyce 前面可能多 index）
        if len(nums) >= 3:
            v, q, qb = nums[-3:]
            Vnoise.append(v)
            Q.append(q)
            QB.append(qb)

Vnoise = np.array(Vnoise)
Q = np.array(Q)
QB = np.array(QB)

print(f"Loaded {len(Q)} DC points")

# ===============================
# 2. Butterfly plot (paper style)
# ===============================
plt.figure(figsize=(4.5, 4.5))

plt.plot(Q, QB, 'k', lw=2)
plt.plot(QB, Q, 'k', lw=2)

plt.xlabel("V(Q) [V]")
plt.ylabel("V(QB) [V]")
plt.title("DC_disturbance_curve")

plt.axis("equal")
plt.xlim(0, 0.6)
plt.ylim(0, 0.6)

plt.tight_layout()
plt.show()
