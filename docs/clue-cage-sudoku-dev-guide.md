Clue-Cage Sudoku Solver Engineering Guide

本篇文档配合 docs/clue-cage-sudoku.md（规格说明）使用，聚焦工程实现、剪枝与可观测性方案，便于调试与验证。

1) 目标与范围
- 实现 9×9 数独变体求解器，支持：基础数独、Numbered Rooms（指针线）、Killer Cages（笼和）。
- 纯标准库实现；默认 cage_all_different = false（可配置）。
- 提供 `solve(puzzle) -> grid` 与 `verify(puzzle, grid) -> (ok, errors)`；支持 CLI 调试与统计输出。

2) 代码结构（src/）
- `clue_cage_sudoku/__init__.py`：导出 `solve`、`verify`、`load_puzzle`。
- `clue_cage_sudoku/parser.py`：解析 JSON（docs/clue-cage-sudoku-data.json）为 `Puzzle`。
- `clue_cage_sudoku/model.py`：基本类型、网格/域（1-based 索引约定）。
- `clue_cage_sudoku/constraints.py`：行/列/宫同伴关系，指针线 L[1..9] 建立等。
- `clue_cage_sudoku/propagation.py`：传播器（基础去除、隐性单、笼可行元组剪枝、指针正反向支持）。
- `clue_cage_sudoku/solver.py`：MRV 回溯 + 传播，节点/时间上限与心跳。
- `clue_cage_sudoku/verify.py`：三类约束校验与错误细节。
- `clue_cage_sudoku/debug.py`：打印网格、统计与心跳格式化。
- `clue_cage_sudoku/main.py`：CLI 入口（`python -m clue_cage_sudoku ...`）。

3) 传播与剪枝策略（与规格第 4 节呼应）
- 基础数独：
  - 裸单（单候选）传播；
  - 隐性单（某行/列/宫某数字仅一处可放）；
  - 同伴去除（同行/同列/同宫排除已赋值）。
- 笼（Killer Cages）：
  - 边界检查：sum_min/sum_max；
  - 位置级候选削减：枚举可行元组（笼大小≤5，可承受），将每格域缩为“在至少一个可行元组中出现的值”。当 `cage_all_different=true` 时，枚举去重。
- 指针线（Numbered Rooms）：
  - 正向：过滤 L[1] 的候选 n：若 d ∉ Dom(L[n]) 或 (n==1 且 d!=1) 或 L[n] 已定≠d，则删 n；当 L[1] 定 n，强制 L[n]=d。
  - 反向：若不存在 n 使得 L[n] 能为 d，则从 L[n] 移除 d；若 L[k] 定为 d，则要求 k ∈ Dom(L[1]) 并收缩 Dom(L[1]) 到 {k}（或与其他可能 k 求交）。
- 事件与收敛：循环传播直到不再改变或触达时间/节点上限。

4) 搜索策略（与规格第 4.3 节呼应）
- 变量选择：MRV（最小域）+ 度数打平（行列宫+笼+指针线参与度）。
- 值顺序：简单 LCV 近似（尝试“对同行列宫+笼+指针线删除候选更少”的值优先）。
- 限制：`--max-seconds` 与 `--max-nodes`；在超限时返回中间状态与统计。

5) CLI 与可观测性
- 关键参数：
  - `--propagate-only`：仅传播；
  - `--max-seconds N`、`--max-nodes N`：时间/节点上限；
  - `--trace`：启用心跳；`--trace-interval S`：心跳间隔秒；
  - `--stats`：结束时打印统计；
  - `--strategy`：逗号分隔开关，示例：`cage_support,pointer_back,hidden_single`。
- 心跳信息（每 S 秒）：
  - 时间、回溯节点、赋值数、候选删除数；
  - 当前决策深度、待处理队列规模（内部近似）；
  - 域分布计数（size=1..9）；
  - 约束工作量：笼重算次数/命中率、指针触发次数、隐性单命中。

6) 验证与回归
- `verify(puzzle, grid)` 按 docs/clue-cage-sudoku.md 第 5 节要求返回错误详情：
  - 行/列/宫重复；
  - 笼和不匹配（期望 vs 实得，笼索引/坐标）；
  - 指针线违规（side/index/d，N 与 L[N] 观测值）。
- 回归方式：
  - 传播回归：`--propagate-only --stats` 秒级反馈；
  - 有限搜索：`--max-seconds 30 --trace --trace-interval 5` 观察收敛趋势；
  - 策略 A/B：通过 `--strategy` 切换剪枝组件，比较 stats。

7) 性能开关与安全边界
- 策略位（可组合）：
  - `hidden_single`、`locked_candidate`（行宫/列宫锁定，初版可不启或仅实现基础版）、
  - `cage_support`（笼可行元组）
  - `pointer_back`（指针反向支持）。
- 默认启用：`hidden_single,cage_support,pointer_back`。
- 安全退出：命中时间/节点上限或 Ctrl-C 时，打印最后心跳与统计，然后退出。

8) 运行示例
- 仅传播并打印统计：
  `python -m clue_cage_sudoku --puzzle docs/clue-cage-sudoku-data.json --propagate-only --stats`
- 30 秒限时、5 秒心跳：
  `python -m clue_cage_sudoku --puzzle docs/clue-cage-sudoku-data.json --max-seconds 30 --trace --trace-interval 5 --stats`

附注：本指南与规格文档互为参照，规格定义了约束语义与 API，本指南定义工程落地与可观测性手段。

