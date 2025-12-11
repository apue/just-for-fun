🌞🌍 Solar–Earth Two-Body Model (v1.0)

A Modeling Specification Document

⸻

1. Problem Definition（问题定义）

本模型用于模拟太阳–地球两体系统的轨道运动，目标是：
	•	复现地球的近似椭圆轨道
	•	得到轨道周期（约 1 年）
	•	展示速度变化、能量守恒情况
	•	演示不同数值积分方法（Euler vs Verlet）的效果差异
	•	为未来扩展（加入月球、摄动等）打下基础

模拟维度：二维平面（x, y），忽略 z。
时间尺度：模拟 1–10 年的轨道演化。

⸻

2. Model Assumptions（模型假设）
	1.	太阳与地球均视为点质量。
	2.	不考虑太阳的运动（太阳固定在原点）。
（这是常见入门近似，误差很小。）
	3.	不考虑潮汐力、相对论效应、太阳质量损失等。
	4.	不考虑其他行星对地球轨道的扰动。
	5.	不考虑地球自转、倾角等因素，专注轨道动力学。

⸻

3. State Variables（状态变量）

地球的状态用以下变量表示：

Symbol	Meaning	Unit
x, y	地球位置（二维）	AU
vx, vy	地球速度	AU / year
m	地球质量	Earth mass (unused in two-body)

太阳质量固定为 1（规范化单位，见下一节）。

⸻

3.b Units & Normalization（单位与归一化）

为简化模型，采用规范化单位：
	•	距离单位：1 AU
	•	时间单位：1 年
	•	质量单位：1 太阳质量 M⊙

因此：
	•	地球轨道半径 ≈ 1
	•	轨道周期 ≈ 1
	•	太阳质量 = 1
	•	引力常数 G = 4π²

这是非常经典的天体力学单位体系，使轨道方程形式更简单。

初始条件（建议）
	•	位置：
r_0 = (1, 0)\ \text{AU}
	•	速度：
v_0 = (0, 2\pi)\ \text{AU/year}

这对应一个完美圆轨道（可用于验证模型是否正确）。

之后你可以加入椭圆轨道的参数作为扩展。

⸻

4. Physics Equations（物理方程）

4.1 引力加速度

太阳固定在原点：

\vec{a} = - \frac{GM_{\odot}}{r^3} \vec{r}

在规范化单位下：
	•	M_{\odot} = 1
	•	G = 4\pi^2

因此：

\vec{a} = - 4\pi^2 \frac{\vec{r}}{|\vec{r}|^3}

⸻

4.2 状态演化 ODE

\frac{d\vec{r}}{dt} = \vec{v}
\frac{d\vec{v}}{dt} = \vec{a}

⸻

5. Numerical Method（数值积分方法）

5.1 时间步 Δt

Δt = 1/365 年（每天一步）

⸻

5.2 Euler Method

（用于演示不稳定性，不推荐长期使用）

v_{t+\Delta t} = v_t + a_t \Delta t

r_{t+\Delta t} = r_t + v_t \Delta t

特点：
	•	简单
	•	大 dt 时能量明显漂移（容易跑飞）

⸻

5.3 Leapfrog / Verlet Method

推荐方法。

公式：

v_{t+\frac{1}{2}} = v_t + \frac{1}{2} a_t \Delta t

r_{t+\Delta t} = r_t + v_{t+\frac{1}{2}} \Delta t

v_{t+\Delta t} = v_{t+\frac{1}{2}} + \frac{1}{2} a_{t+\Delta t} \Delta t

特点：
	•	能量几乎守恒
	•	长期轨道稳定
	•	天文学中常用的辛积分法

⸻

6. Pseudocode（伪代码）

initialize r = (1, 0)
initialize v = (0, 2π)

for each simulation step:
    compute a = -4π² * r / |r|^3
    # leapfrog:
    v_half = v + 0.5 * a * dt
    r = r + v_half * dt
    compute a_new = -4π² * r / |r|^3
    v = v_half + 0.5 * a_new * dt
    record r, v


⸻

7. Visualization Plan（可视化）

7.1 Space Scale（空间缩放）

屏幕大小：800 × 800 px
映射规则：
	•	world_x ∈ [-1.5, 1.5] AU
→ screen_x = 400 + world_x * (400 / 1.5)

可视化内容：
	•	地球轨道路径（线）
	•	地球当前点（圆点）
	•	太阳固定在中心

⸻

7.2 Time Playback Scale（时间播放缩放）

模拟每一步可能代表：
	•	1 天、或
	•	0.5 天、或
	•	0.1 天

例如：
	•	300 帧播放 1 年 → speed = 365/300 ≈ 1.2 天/帧
	•	60 FPS 播放时 1 年约 5 秒完成

⸻

7.3 其他图形输出
	•	轨道能量随时间的变化
	•	速度大小 vs 时间
	•	r(t) vs 时间（半径变化）

这些图可以用于数值方法和 dt 的对比实验。

⸻

8. Validation（模型验证）

本模型的正确性可以通过以下标准验证：

✔ 轨道周期 ≈ 1 年

（检查圆一圈的时间）

✔ 轨道形状为圆（或接近初始条件给定的椭圆）

✔ 能量守恒良好
	•	Euler 会有明显漂移
	•	Leapfrog 几乎不漂移

✔ 开普勒第二定律

地球速度应在近日点最大。

⸻

9. Extensions（扩展方向）

你可以基于当前模型，继续加入更复杂的物理：

⭐ 加入月球（三体系统）

⭐ 使用真实初始条件（近日点、地球椭圆轨道）

⭐ 加入太阳的运动（质心坐标系）

⭐ 加入 J2 摄动（让轨道发生岁差）

⭐ 模拟多行星（太阳系小规模 N-body）

⭐ 对比不同数值方法（Euler, RK4, Leapfrog）

⭐ 研究长期稳定性（误差随年份积累）

⸻

10. References（参考资料）
	•	NASA JPL Solar System Dynamics
	•	常规模拟单位：https://en.wikipedia.org/wiki/Astronomical_system_of_units
	•	Kepler’s laws of planetary motion
	•	Symplectic integrators, Leapfrog method

⸻
