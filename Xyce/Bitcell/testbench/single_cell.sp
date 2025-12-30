* SRAM_9T_SINGLE_CELL_TEST_BENCH
.title_9T_SRAM_Single_Cell_Functionality_Test

*** 1. 环境与模型包含 ***
.TRAN 10ps 40ns
.options samples numsamples=10
.include "tmp_mc.spice"

*** 2. 电源定义 ***
.param VDD_VAL=0.6V
VVDD VDD 0 DC {VDD_VAL}
VVSS VSS 0 DC 0V

*** 3. 激励信号：严格复现图(b)时序 ***
* 周期定义: 0-10n (Hold), 10-20n (Read), 20-30n (Write-0), 30-40n (Write-1)

* WL: 只在 Hold 期间为低，其余时间激活
VWL  WL  0 PWL(0n 0V 10n 0V 10.01n {VDD_VAL} 40n {VDD_VAL})

* WWLA: 仅在 Write-0 (20-30n) 产生高脉冲
VWWLA WWLA 0 PWL(0n 0V 20n 0V 20.1n {VDD_VAL} 29.9n {VDD_VAL} 30n 0V)

* WWLB: 默认高，仅在 Write-1 (30-40n) 产生负辅助 (Negative Assist)
* 注意：这里模拟图中的 Negative Assist，拉到 -0.1V
VWWLB WWLB 0 PWL(0n {VDD_VAL} 30n {VDD_VAL} 30.1n -0.1V 39.9n -0.1V 40n {VDD_VAL})

* BL: 模拟读写操作的位线电平
* Read: 预充高; Write-0: 拉低; Write-1: 拉高
VBL  BL  0 PWL(0n {VDD_VAL} 20n {VDD_VAL} 20.1n 0V 30n 0V 30.1n {VDD_VAL} 40n {VDD_VAL})

*** 4. 实例化单个 9T Cell ***
.subckt SRAM_9T_CELL VDD VSS BL WL WWLA WWLB Q QB VX
* 参数定义：l=50nm, w=晶体管宽度

* --- 寄生 RC 建模 (仿照 6T Demo) ---
RR_BL_0   BL   BL_end   100Ohm
CCg_BL_0  BL_end 0     0.001pF
RR_WL_0   WL   WL_end   100Ohm
CCg_WL_0  WL_end 0     0.001pF
RR_WWLA_0 WWLA WWLA_end 100Ohm
CCg_WWLA_0 WWLA_end 0  0.001pF
RR_WWLB_0 WWLB WWLB_end 100Ohm
CCg_WWLB_0 WWLB_end 0  0.001pF
RR_Q_0    Q    Q_end    100Ohm
CCg_Q_0   Q_end 0      0.001pF
RR_QB_0   QB   QB_end   100Ohm
CCg_QB_0  QB_end 0     0.001pF

* --- 左侧支路 (节点 Q_end) ---
* 上拉堆叠 (Pull-Up Left). PUL1 (受 QB 控制) 和 PUL2 (受 WWLA 控制)
MPUL1 net_pul1 QB_end VDD VDD PMOS_VTG l=5e-08 w=9e-08
MPUL2 Q_end WWLA_end net_pul1 VDD PMOS_VTG l=5e-08 w=9e-08

* 下拉堆叠 (Pull-Down Left). PDL1 (受 WWLB 控制) 和 PDL2 (受 QB 控制)
MPDL1 Q_end WWLB_end net_pdl1 VSS NMOS_VTG l=5e-08 w=9e-08
MPDL2 net_pdl1 QB_end VSS VSS NMOS_VTG l=5e-08 w=9e-08

* 存取管 (Pass Gate). 受 WL 控制连接 BL 与 Q
MPG   Q_end WL_end BL_end VSS NMOS_VTG l=5e-08 w=1.35e-07

* --- 右侧支路 (节点 QB_end) ---
* 标准上拉 (Pull-Up Right). 受 Q 控制
MPUR  QB_end Q_end VDD VDD PMOS_VTG l=5e-08 w=9e-08

* 下拉堆叠与反馈 (Pull-Down Right). PDR1, PDR2 (受 Q 控制) 和 NF (反馈管)
MPDR1 QB_end Q_end VX VSS NMOS_VTG l=5e-08 w=9e-08
MPDR2 VX Q_end VSS VSS NMOS_VTG l=5e-08 w=9e-08

* 反馈管 (NF). 连接 VX 节点与 WWLB 偏置，受 QB 控制
MNF   VX QB_end WWLB_end VSS NMOS_VTG l=5e-08 w=9e-08

.ends SRAM_9T_CELL
XCELL VDD VSS BL WL WWLA WWLB Q QB VX SRAM_9T_CELL

*** 5. 初始状态设置 ***
* 假设初始存储数据为 '1' (Q=High, QB=Low)
.ic V(Q)=0.6V V(QB)=0V V(VX)=0V

*** 6. 观测与测量 ***
.PRINT TRAN V(WL) V(WWLA) V(WWLB) V(BL) V(Q) V(QB)

* 测量写 0 延迟 (Q 从 0.6V 降至 0.1V)
.meas TRAN T_write0_delay TRIG V(WWLA) VAL=0.3 RISE=1 TARG V(Q) VAL=0.1 FALL=1
* 测量写 1 延迟 (Q 从 0V 升至 0.5V)
.meas TRAN T_write1_delay TRIG V(WWLB) VAL=0.3 FALL=1 TARG V(Q) VAL=0.5 RISE=1

.end