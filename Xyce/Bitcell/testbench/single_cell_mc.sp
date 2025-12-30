* 9T SRAM Single Cell Monte Carlo Test Bench (1000 Samples)

*** 1. 环境与模型包含 ***
.include "tmp_mc.spice"

*** 2. 仿真配置 - 启用表达式采样 ***
* 必须开启 useExpr=true 才能让参数在每一轮蒙卡中重新计算
.SAMPLING useExpr=true 
.options samples numsamples=1000

*** 3. 变量定义 ***
.param VDD_VAL = 0.6V

*** 4. 仿真控制 ***
.TRAN 1.0000e-11 6.0000e-08
.OPTIONS OUTPUT INITIAL_INTERVAL=1.0000e-11

*** 5. 电源与激励信号 ***
VVDD VDD 0 DC {VDD_VAL}
VVSS VSS 0 DC 0V

* 激励波形保持不变
VWL   WL   0 PWL(0n 0V 10n 0V 10.05n {VDD_VAL} 40n {VDD_VAL})
VWWLA WWLA 0 PWL(0n 0V 20n 0V 20.05n {VDD_VAL} 29.95n {VDD_VAL} 30n 0V)
VWWLB WWLB 0 PWL(0n {VDD_VAL} 30n {VDD_VAL} 30.05n -0.1V 39.95n -0.1V 40n {VDD_VAL})
VBL   BL   0 PWL(0n {VDD_VAL} 20n {VDD_VAL} 20.05n 0V 30n 0V 30.05n {VDD_VAL} 40n {VDD_VAL})

*** 6. 实例化 9T Cell ***
.subckt SRAM_9T_CELL VDD VSS BL WL WWLA WWLB Q QB
* 这里的电阻和电容可以根据你的 RC 网络设置进行调整
RR_BL  BL   BL_i  10
RR_WL  WL   WL_i  10
RR_WA  WWLA WA_i  10
RR_WB  WWLB WB_i  10

* 核心存储单元管子
MPUL1 net_pul1 QB VDD VDD PMOS_VTG l=5e-08 w=9e-08
MPUL2 Q WA_i net_pul1 VDD PMOS_VTG l=5e-08 w=9e-08
MPDL1 Q WB_i net_pdl1 VSS NMOS_VTG l=5e-08 w=9e-08
MPDL2 net_pdl1 QB VSS VSS NMOS_VTG l=5e-08 w=9e-08
MPG   Q WL_i BL_i VSS NMOS_VTG l=5e-08 w=1.35e-07

MPUR  QB Q VDD VDD PMOS_VTG l=5e-08 w=9e-08
MPDR1 QB Q VX VSS NMOS_VTG l=5e-08 w=9e-08
MPDR2 VX Q VSS VSS NMOS_VTG l=5e-08 w=9e-08
MNF   VX QB WB_i VSS NMOS_VTG l=5e-08 w=9e-08
.ends SRAM_9T_CELL

XCELL VDD VSS BL WL WWLA WWLB Q QB SRAM_9T_CELL

*** 7. 初始状态与测量 ***
.ic V(Q)=0.6V V(QB)=0V

* 测量写 0 延时 (TRIG: WWLA上升至0.3V, TARG: Q下降至0.3V)
.meas TRAN T_WRITE0_DELAY TRIG V(WWLA) VAL=0.3 RISE=1 TARG V(Q) VAL=0.3 FALL=1
* 测量写 1 延时 (TRIG: WWLB下降至0.3V, TARG: Q上升至0.3V)
.meas TRAN T_WRITE1_DELAY TRIG V(WWLB) VAL=0.3 FALL=1 TARG V(Q) VAL=0.3 RISE=1

* 关闭波形打印以节省 1000 次仿真产生的海量存储空间
* 如果需要调试，可以取消下面这一行的注释
* .PRINT TRAN V(WL) V(WWLA) V(WWLB) V(Q) V(QB)

.end