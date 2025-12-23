# OpenYield-9T-SRAM

## 项目简介

本项目基于 OpenYield / PySpice 自动化电路设计流程，实现并验证一种 **9T SRAM 单元拓扑** 的完整晶体管级建模、阵列构建与电路级验证流程。  
项目以 SRAM Macro 为目标对象，覆盖从 9T SRAM bitcell 建模、阵列级集成、外围电路适配，到 PVT 与 Monte Carlo 良率分析的完整前端设计过程。


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
.
├── cell/
│   └── sram_9t_cell.py
├── array/
│   ├── sram_array.py
│   └── sram_core_9t.py
├── peripheral/
│   ├── decoder.py
│   ├── precharge.py
│   ├── sense_amp.py
│   ├── write_driver.py
│   └── wl_driver.py
├── testbench/
│   ├── functional_tb.py
│   ├── snm_tb.py
│   ├── timing_tb.py
│   └── monte_carlo_tb.py
├── scripts/
│   └── run_simulation.py
└── README.md
