# OpenYield 9T SRAM ST

这是一个专注于 **成品率优化 (Yield Optimization)** 与 **高稳定性 (Stability)** 的 9T SRAM 存储单元设计项目。

## 📌 项目简介
本项目提供了一个完整的 9T SRAM 位单元 (Bitcell) 设计方案。相比于传统的 6T SRAM，该 9T 结构通过增加晶体管来解耦读/写路径，从而在低电压工作环境下显著提升静态噪声容限 ($SNM$) 和成品率。

* **技术节点**: (例如: SkyWater 130nm / FreePDK 45nm)
* **核心特性**: 高成品率、单端/差分读取、低功耗。
* **分析工具**: Hspice / Spectre / Python (Data Analysis)

---

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
