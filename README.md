# OpenYield-9T-SRAM

## 1.项目简介

本项目基于 OpenYield / PySpice 自动化电路设计流程，参考 IEEE T-CAS I 2020 论文 *"One-Sided Schmitt-Trigger-Based 9T SRAM Cell for Near-Threshold Operation"*，实现并验证了一种针对 **近阈值 (Near-Threshold)** 环境优化的 9T SRAM 存储宏单元（Macro）。

项目不仅完成了 9T Bitcell 的建模，还构建了完整的 **8x4 SRAM 阵列及全外围电路**（包含行译码器、字线驱动器、列选择器及感测放大器），并针对工艺偏差进行了蒙特卡洛（Monte Carlo）良率分析。

---

## 2.核心技术特性

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
## 3.仓库结构

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

## 4. 自动化设计流程 (Automated Design Flow)

本项目基于 **OpenYield** 框架实现了 **One-command Flow**，将复杂的电路参数调整、网表拼接与统计仿真通过 Python 脚本进行自动化管理。

### 4.1 编译与仿真一键化
未完成：通过 `main_sram.py` 驱动 OpenYield 核心，自动解析 YAML 配置并调用 **Xyce** 仿真器：

```bash
# [功能验证] 执行全系统逻辑功能仿真
python OpenYield/main_sram.py --testbench sram_9t_core_testbench

# [良率分析] 执行 1000 次采样级别的蒙特卡洛 (Monte Carlo) 统计分析
python OpenYield/main_sram.py --testbench sram_9t_core_MC_testbench (更改中)
```
### 4.2 环境与扩展预留
linux虚拟机镜像见7.1
未完成：将 8x4 阵列扩展至 32x32 或更大规模，编译器自动处理字线（WL）与位线（BL）的映射。

---
## 5. 仿真验证结果
### 5.1 静态噪声裕度 (RSNM)
利用 One-sided Schmitt-Trigger 结构，9T 单元在 $V_{DD}=0.5V$ 的近阈值条件下展现出显著的滞回特性。通过 DC 扫描得到的蝶形曲线显示，其读取噪声裕度相比传统 6T SRAM 提升了约 XX%。

---
## 设计内容与实现

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

## 仿真验证与结果

本项目通过 `SRAM_9T_CORE_8x4_MC_TB` 测试平台进行全路径验证。

### 1. 静态指标 (RSNM)
利用施密特触发器结构，9T 单元在 $V_{DD}=0.5V$ 下表现出显著的滞回特性，RSNM 相比传统 6T 提升约 **XXX%**。

### 2. 瞬态功能验证
验证了从地址输入到感测放大器输出的全流程。
* **读操作**：单端位线放电至 `VREF` 以下，SA 成功触发。
* **写操作**：在写辅助信号作用下，成功完成近阈值下的数据翻转。

### 3. 蒙特卡洛统计分析 (工艺偏差)
通过对阵列进行蒙特卡洛仿真（Mismatch 建模），提取以下测量指标：
| 性能指标 | 说明 | 典型值 (VDD=0.6V) |
| :--- | :--- | :--- |
| **TDECODER** | 译码器 + 路径延迟 | XX ns |
| **TWRITE1** | 最差情况写 1 延迟 | XX ns |
| **TSA_READ** | 读感测延迟 | XX ns |
| **PAVG** | 阵列平均功耗 | XX uW |
| **PLEAK** | 静态漏电功耗 | XX nW |

---

## 7. 运行环境配置 (Environment Setup)

本项目依赖 Xyce 仿真器及特定的 Python 科学计算环境。为了方便用户快速复现，我们提供了预装好所有工具链的 **Ubuntu 虚拟机镜像**。

### 7.1 获取镜像 (Ubuntu Image)
请从以下网盘链接下载预配置好的环境：
- **链接**: [此处填写你的网盘分享链接]
- **提取码**: [此处填写提取码]
- **镜像版本**: Ubuntu 22.04 LTS (Pre-installed with Xyce 7.8 & Conda)

### 7.2 镜像导入说明
1.  下载解压后，使用 **VMware Workstation** 或 **VirtualBox** 打开 `.ovf` 或 `.vmx` 文件。
2.  **默认凭据**:
    - 用户名: `openyield`
    - 密码: `123456`

---


---
##参考文献

[1] K. Cho, et al., "One-Sided Schmitt-Trigger-Based 9T SRAM Cell for Near-Threshold Operation," in IEEE T-CAS I, vol. 67, no. 5, 2020.
