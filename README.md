# OpenYield-9T-SRAM

## 项目简介

本项目基于 OpenYield / PySpice 自动化电路设计流程，参考 IEEE T-CAS I 2020 论文 "One-Sided Schmitt-Trigger-Based 9T SRAM Cell for Near-Threshold Operation"，实现并验证了一种针对近阈值（Near-Threshold）环境优化的 9T SRAM 单元拓扑。  
项目以 SRAM Macro 为目标对象，覆盖从 9T SRAM bitcell 建模、阵列级集成、外围电路适配，到 PVT 与 Monte Carlo 良率分析的完整前端设计过程。

## 核心技术特性


本项目复现了论文中解决近阈值 SRAM 不稳定问题的三大核心设计：
1.单边施密特触发器 (One-Sided ST) 结构：通过反馈晶体管提升读取状态下的节点翻转阈值，显著增强读取稳定性（Read Stability）。
2.辅助写偏置策略 (Write Assist Scheme)：利用 WWLA 和 WWLB 信号动态调整施密特触发器的翻转阈值（Trip Voltage），解决近阈值下写入困难的问题。
3.无回写位交织支持 (Bit-Interleaving without Write-back)：利用单端读取（Single-Ended Read）特性，在无需复杂回写电路的情况下，有效抑制半选单元（Half-Selected Cells）的干扰。
---

## 项目背景

随着低功耗与近阈值计算需求的增长，传统 SRAM 结构在稳定性与可扩展性方面面临挑战。  
9T SRAM 通过引入额外晶体管与独立读路径，在读稳定性、失配鲁棒性等方面具有潜在优势，适合用于对可靠性要求较高的存储与存算相关应用场景。

本项目旨在基于自动化设计工具链，对 9T SRAM 拓扑进行系统建模与验证，探索其在工程化 SRAM 设计流程中的实现方式。

---

## 设计目标

- 构建可参数化的 9T SRAM 单元晶体管级模型  
- 在自动化流程中完成 9T SRAM 阵列的构建与集成  
- 适配 9T SRAM 的读写外围电路与时序控制  
- 完成静态、动态及统计意义下的电路级验证  
- 形成具备工程复用价值的 SRAM 前端设计流程  

---

## 设计内容

### 1. 9T SRAM 单元建模
- 基于 PySpice 的晶体管级参数化描述
- 明确 9T SRAM 的读写路径与控制信号
- 支持晶体管尺寸与工艺模型配置

### 2. SRAM 阵列构建
- 支持行列规模可配置的 SRAM 阵列生成
- 兼容标准地址译码与字线控制结构
- 面向 SRAM Macro 的阵列级设计

### 3. 外围电路设计
- 写驱动与写位线控制
- 读位线预充电与感测放大电路
- 字线与读字线驱动电路
- 时序控制与非重叠信号设计

### 4. 仿真与验证
- 基本功能仿真（读 / 写 / 保持）
- 静态指标分析（SNM、写裕量）
- 动态指标分析（读延时、能耗）
- PVT 条件扫描
- Monte Carlo 失配仿真与良率统计

---

## 工具与环境

- Python 3.x
- PySpice
- Ngspice / HSPICE（可选）
- OpenYield 自动化设计框架
- 开源工艺 PDK（如 ASAP7、sky130）

---

## 仓库结构（示例）

```text
sram-9t-macro/
├── cell/
│   └── sram_9t_cell.py             # 9T bitcell 参数化建模
├── array/
│   ├── sram_array.py                # 阵列生成逻辑
│   └── sram_core_9t.py             # 9T SRAM 阵列核心
├── peripheral/
│   ├── decoder.py
│   ├── precharge.py
│   ├── sense_amp.py
│   ├── write_driver.py
│   └── wl_driver.py
├── testbench/
│   ├── functional_tb.py             # 功能验证
│   ├── timing_tb.py                 # 时序验证
│   ├── snm_tb.py                    # 静态噪声裕度测试
│   └── monte_carlo_tb.py            # 失配与良率仿真
├── scripts/
│   └── run_simulation.py            # 仿真运行脚本
├── docs/
│   └── diagram.png                  # 电路结构示意图
├── .gitignore
└── README.md
