

# 🌌 AstroModel Template（v1.0）

⸻

# 1. Problem Definition（问题定义）

简要描述要模拟的系统：
	•	系统包含哪些天体？
	•	目标是什么？（轨道？能量？长期演化？稳定性？）
	•	模拟时间尺度？（天、年、秒）

Example：
模拟太阳–地球两体系统，目的是再现椭圆轨道和速度变化规律。

⸻

# 2. Model Assumptions（模型假设）

清楚列出简化假设：
	•	天体视为点质量
	•	忽略潮汐力
	•	忽略相对论效应
	•	引力常数 G 为常数
	•	轨道平面为二维（如适用）

这些决定模型的现实程度，也影响未来如何扩展。

⸻

# 3. State Variables（状态变量定义）

系统的“最小描述参数集”。
每个天体通常包含：

r = (x, y, z)
v = (vx, vy, vz)
m = mass

可以写成表格：

Symbol	Meaning
x, y, z	位置坐标（m）
vx, vy, vz	速度（m/s）
m	质量（kg）


⸻

# 4. Physics Equations（物理方程）

4.1 力（Force）

例：万有引力
\vec{F} = -\frac{G m_1 m_2}{r^2}\hat{r}

4.2 加速度（Acceleration）

\vec{a} = \frac{\vec{F}}{m}

4.3 状态演化 ODE

\frac{d\vec{r}}{dt} = \vec{v}
\frac{d\vec{v}}{dt} = \vec{a}

4.4 能量（可选）

E = \frac12 mv^2 - \frac{GMm}{r}

能量检查是后期验证数值稳定性的重要手段。

⸻

# 5. Numerical Method（数值方法）

解释你如何把微分方程变成能被计算机执行的离散步骤。

必须写清楚：

5.1 时间步 Δt

单位：秒
选择依据：
	•	稳定性
	•	轨道尺度
	•	速度变化

5.2 积分方法

常见方法：

◉ Euler 法（最简单）
v_{t+\Delta t} = v_t + a_t \Delta t
r_{t+\Delta t} = r_t + v_t \Delta t

◉ Verlet / Leapfrog（天文模拟最常用）
写出它的更新公式与优点（能量更稳定）。

5.3 误差、稳定性

说明：
	•	Δt 过大 → 轨道发散
	•	Verlet 比 Euler 稳定性高
	•	能量漂移如何检查

⸻

# 6. Pseudocode（伪代码）

用逻辑表达模拟循环，不写具体语言。

initialize state (r, v, m)
set time_step dt
for each step:
    compute gravitational acceleration
    update velocity
    update position
    record trajectory

如果多体：

for i in bodies:
    a[i] = sum_over_j(G*m_j*(r_j - r_i)/|r_j - r_i|^3)

重点不是代码，而是逻辑结构清晰。

⸻

# 7. Visualization Plan（可视化规划）

说明如何呈现模型输出：
	•	轨道图（x vs y）
	•	速度大小随时间变化
	•	能量随时间变化
	•	动画（可选）
	•	3D 轨道（可选）

你的 notebook 可以按这个顺序组织：

Section 1: Simulation setup
Section 2: Run simulation
Section 3: Plot trajectory
Section 4: Plot energy drift
Section 5: Animation (optional)


⸻

# 8. Validation（验证）

你应验证模型的正确性，例如：
	•	地球周期是否接近 365 天
	•	轨道是否稳定
	•	能量是否基本守恒
	•	速度在近日点更大（符合开普勒第二定律）

通过可视化图判断模型是否合理。

⸻

# 9. Extensions（扩展）

写出未来如何扩展模型：
	•	加月球 → 三体系统
	•	引入 J2 摄动
	•	加入潮汐力 → 月球远离地球
	•	引入太阳质量损失
	•	引入暗物质额外势场

目的：形成“可持续成长”的模型体系。

⸻

# 10. Notes & References（备注与参考）

例如：
	•	NASA 常数
	•	JPL 天体数据
	•	教科书或 lecture notes 链接

