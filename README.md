# OpenYield-9T-SRAM

## 1. 项目简介

本项目基于 OpenYield / PySpice 自动化电路设计流程，参考 IEEE T-CAS I 2020 论文 *"One-Sided Schmitt-Trigger-Based 9T SRAM Cell for Near-Threshold Operation"*，实现并验证了一种针对 **近阈值 (Near-Threshold)** 环境优化的 9T SRAM 存储宏单元（Macro）。

项目不仅完成了 9T Bitcell 的建模，还构建了完整的 **8x4 SRAM 阵列及全外围电路**（包含行译码器、字线驱动器、列选择器及感测放大器），并针对工艺偏差进行了蒙特卡洛（Monte Carlo）良率分析。

---

## 2. 核心技术特性

### 2.1 存储宏单元 (SRAM Macro) 集成
项目实现了完整的存储宏系统，利用单端读取特性优化了近阈值操作：
- **Row Decoder**: 3-to-8 译码器，负责行地址选通。
- **Wordline Driver**: 支持同步产生 `WWLA`（写0辅助）与 `WWLB`（写1辅助）偏置信号。
- **Sense Amplifier (SA)**: 电压锁存型单端感测放大器，适配单端位线放电。
- **Column MUX**: 2选1列选择逻辑，支持位交织（Bit-Interleaving）架构。
### 2.2 9T ST-SRAM 核心技术
本项目复现了论文中解决近阈值 SRAM 不稳定问题的核心设计：
- **单边施密特触发器 (One-Sided ST) 结构**：通过反馈晶体管提升读取状态下的节点翻转阈值，显著增强读取稳定性（Read Stability）。
- **动态写偏置策略 (Write Assist Scheme)**：利用字线驱动同步产生的 `WWLA`（升压）和 `WWLB`（负偏置）信号，动态调整施密特触发器的翻转阈值（Trip Voltage），攻克近阈值下写入困难的瓶颈。
- **系统级集成与单端感测**：针对 9T 的单端位线（Single-Ended BL）特性，设计了带外部参考电平（VREF）的电压锁存型感测放大器。
- **无回写位交织支持**：利用单端读取特性，在无需复杂回写电路的情况下，有效抑制半选单元（Half-Selected Cells）干扰。

---
## 3. 仓库结构

```text
OpenYield-9T-SRAM/
.
├── 📂 OpenYield/               # 自动化设计与编译器核心
│   ├── 📂 sram_compiler/       # SRAM 编译器
│   │   ├── 📂 config_yaml/     # 各模块参数配置文件 (YAML)
│   │   ├── 📂 subcircuits/     # 参数化电路类实现 (Python)
│   │   └── 📂 testbenches/     # 自动化仿真脚本 (MC/Function)
│   └── main_sram.py            # 编译器主入口脚本
│
└── 📂 Xyce/                    # 核心电路分析与验证 (物理层)
|   ├── 📂 Bitcell/             # 单元级分析 (RSNM, DC Disturbance)
|   └── 📂 Macro/               # 宏模块级分析 (8x4 Array, Peripheral)
|       ├── 📂 results/         # 仿真波形图与原始数据 (.prn, .mt0)
|       └── 📂 scripts/         # 针对 Xyce 输出结果的专用绘图工具
└── 📂 docs/                    # 参考文献与技术文档
└── README.md
```
---

## 4. 核心验证流程：基于 Xyce 的电路分析
本项目目前专注于 9T ST-SRAM Bitcell 的物理特性验证。通过 Xyce 仿真器，我们对近阈值（Near-Threshold）电压下的稳定性、功能性及可靠性进行了深度评估。
### 4.1 静态噪声裕度分析 (RSNM Analysis)
为了验证单边施密特触发器（One-Sided ST）对读取稳定性的提升，我们设计了 `RSNM.sp` 和 `DC_disturbance_curve.sp` 仿真脚本。

- **仿真方法**：采用双电压源扫描（V-Sweep）方法。在 Xyce 中通过 `.DC` 扫描模拟读取干扰状态，测量存储节点 Q 和 QB 的电压传输曲线（VTC）。
- **技术要点**：
    - **非对称建模**：针对 9T 结构的特殊性，对比了传统 6T 与 9T 的最大内切正方形。
    - **收敛性优化**：通过设置合理的初始条件（`.ic`），确保了在 $V_{DD}=0.5V$ 极低电压下的仿真收敛。
- **结论**：仿真结果显示，9T 结构通过施密特触发器的滞回特性，显著提高了翻转阈值（Trip Voltage）。
### 4.2 瞬态功能验证 (Transient Function Test)
![论文波形](images/论文波形.png)![仿真验证波形](images/仿真验证波形.png)
通过 `single_cell.sp` 脚本验证 9T 单元在完整周期内的动态响应，严格复现论文中的操作逻辑。

- **全路径监控**：实时追踪 `WL` (字线)、`BL` (位线)、`WWLA/B` (辅助信号) 以及 `Q/QB` (存储点) 的电位。
- **辅助逻辑验证**：
    - **Write-0 Assist**: 验证 `WWLA` 升高时对左侧上拉路径（PUL）的削弱效果，显著降低写 0 时延。
    - **Write-1 Assist (Negative Assist)**: 验证 `WWLB` 产生负压脉冲（如 -0.1V）时，对右侧下拉反馈的抑制作用，确保在极低电压下数据仍能顺利翻转。
- **性能测量**：通过 Xyce 的 `.MEASURE` 语句自动提取延迟时间（Write Latency）与功耗数据。
### 4.3 工艺偏差分析 (Monte Carlo Simulation)
为了预测未来宏单元（Macro）的良率，我们利用 Xyce 的统计仿真功能模拟了制造偏差。

- **采样分析**：通过 `single_cell_mc.sp` 执行 **1000 次采样** 的蒙特卡洛迭代（设置 `.SAMPLING useExpr=true`）。
- **关键意义**：评估了随机失配对 RSNM 和写延迟的影响分布，这为后续从单单元扩展到 **8x4 Macro 阵列设计** 奠定了坚实的统计基础。

---
## 5. 仿真复现指南

### 5.1 环境初始化
进入 Ubuntu 镜像或 Linux 环境后（镜像见7.1），加载 Xyce 与 Python 环境：
```bash
source refreshenv
# 进入测试目录
cd Xyce/Bitcell/testbench
# 运行 RSNM 静态扫描
xyce RSNM.sp
python ../scripts/plot_rsnm.py
# 运行 Single Cell 动态功能测试
xyce single_cell.sp
python ../scripts/plot_single_cell.py
```
---
## 6. 设计内容与实现

### 1. 9T SRAM 单元建模
* **左侧支路**：包含上拉堆叠（PUL1/2）和下拉堆叠（PDL1/2），受 `WWLA/B` 调控。
* **右侧支路**：标准上拉（PUR）与带反馈管（NF）的施密特触发下拉结构。
* **寄生建模**：在 Bitcell 内部显式引入了 RC 寄生网络（100Ω/0.001pF），以模拟真实互连线延迟。

### 2. 写辅助逻辑 (Write Assist)
* **写 '0'**：`WWLA` 升高，削弱左侧上拉能力。
* **写 '1'**：`WWLB` 降低（负偏置），削弱右侧下拉反馈，使节点 Q 易于拉高。

### 3. 系统级时序控制
项目设计了复杂的非重叠时序：
1.  **PRECHARGE**：预充位线至 VDD。
2.  **DECODE**：行地址译码，锁定 WL。
3.  **ACCESS/ASSIST**：WL 选通同时，WWLA/B 施加辅助偏置。
4.  **SENSE**：SAE 使能，感测放大器放大位线压差。



---
## 6. Macro与自动化工具
### 已完成Macro的Xyce基本框架搭建
### 未完成自动化flow
---

## 7. 运行环境配置 (Environment Setup)

本项目依赖 Xyce 仿真器及特定的 Python 科学计算环境。为了方便用户快速复现，我们提供了预装好所有工具链的 **Ubuntu 虚拟机镜像**。

### 7.1 获取镜像 (Ubuntu Image)
请从以下网盘链接下载预配置好的环境：
- **链接**: [此处填写你的网盘分享链接]
- **提取码**: [此处填写提取码]
- **镜像版本**: Ubuntu 22.04 LTS (Pre-installed with Xyce 7.8 & Conda)

### 7.2 镜像导入说明
1.  下载解压后，使用 **VMware Workstation**  打开。
2.  **默认凭据**:
    - 用户名: `zhz`
    - 密码: `zhzwcy999`

---
## 参考文献

[1] K. Cho, et al., "One-Sided Schmitt-Trigger-Based 9T SRAM Cell for Near-Threshold Operation," in IEEE T-CAS I, vol. 67, no. 5, 2020.
