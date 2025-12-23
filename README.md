# OpenYield 9T SRAM ST

这是一个基于 9T 近阈值单边施密特触发器 (Schmitt-Trigger) 结构的高成品率 SRAM Macro 设计与全流程验证。

## 📌 项目简介
本项目提供了一个完整的 9T SRAM 位单元 (Bitcell) 设计方案。相比于传统的 6T SRAM，该 9T 结构通过增加晶体管来解耦读/写路径，从而在低电压工作环境下显著提升静态噪声容限 ($SNM$) 和成品率。
## 📖 背景与设计目标
在低电压环境下，传统 6T SRAM 面临严重的稳定性和成品率挑战。本项目实现的 9T 单元通过以下方式优化：
- **解耦读写路径**：消除读干扰 (Read Disturb)。
- **施密特触发器特性**：增强静态噪声容限 ($SNM$)。
* **技术节点**: (例如: SkyWater 130nm / FreePDK 45nm)
* **核心特性**: 高成品率、单端/差分读取、低功耗。
* **分析工具**: Hspice / Spectre / Python (Data Analysis)

---
## 📊 关键仿真结果 (PVT Analysis)
项目完成了详尽的 PVT Corner 仿真，典型数据如下（32x16 Array, TT, 25°C, 1V）：

| Corner | T_DEC (ns) | T_WL (ns) | T_READ (ns) | CLK_min (ns) |
| :--- | :--- | :--- | :--- | :--- |
| **TTG** | 0.0917 | 5.20 | 0.4457 | 0.86 |
| **SSG** | 0.1020 | 5.22 | 0.4825 | 1.10 |
| **FFG** | 0.0834 | 5.19 | 0.4159 | 0.80 |

> 注：详细的温度/电压扫描数据（-40°C 至 125°C）见 `/docs/sim_report.md`。

## 🛠 设计流程 (End-to-End Flow)
1. **Front-End**: 使用 **PySpice** 进行参数化电路建模。
2. **Analysis**: 执行 Monte Carlo 仿真验证 $V_{th}$ 偏移下的稳定性。
3. **Characterization**: 自动化提取 `.lib` 文件的时序与功耗信息。
4. **Back-End**: 基于 **KLayout/Python API** 进行版图自动生成，导出 GDSII 与 LEF。

## 📂 目录结构说明
为了方便开发者和研究者，仓库按以下结构组织：

* 📂 **`docs/`** - 设计规格书、仿真波形图、成品率分析报告。
* 📂 **`spice/`** - 核心电路网表。
    * `cell/` : 9T SRAM 单元电路定义。
    * `peri/` : 预充、译码器等外围电路。
* 📂 **`layout/`** - GDSII 导出文件或版图快照。
* 📂 **`sim/`** - 仿真环境。
    * `monte_carlo/` : 针对 Vth 偏移的蒙特卡罗仿真脚本。
    * `testbench/` : 读/写时序、功耗测试平台。
* 📂 **`scripts/`** - 用于自动化仿真结果后处理的 Python/Tcl 脚本。

---

## 🚀 快速开始
1. **克隆仓库**:
   ```bash
   git clone [https://github.com/您的用户名/OpenYield_9T_SRAM_ST.git](https://github.com/您的用户名/OpenYield_9T_SRAM_ST.git)
2. **文件名称**
- **电路网表**: `/circuit/cell/sram_9t_st.sp`
- **仿真脚本**: `python scripts/run_monte_carlo.py`
- **行为模型**: `/backend/verilog/sram_macro.v`
## 📈 设计亮点
   成品率分析: 经过 $5\sigma$ 蒙特卡罗分析验证。稳定性: $SNM$ 在低电压 ($V_{dd}=0.6V$) 下表现优异。结构优化: 采用 (此处可填 写具体的 ST 结构，如施密特触发器或其他增强结构)。
## ⚖️ 开源协议
本项目采用 Apache 2.0 协议。


---
