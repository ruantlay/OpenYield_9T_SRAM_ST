* 9T SRAM Read SNM Butterfly Plot
.include "/home/zhz/anaconda3/OpenYield_9T_SRAM_ST/sim/9T_sim/tmp_mc.spice"

*** 1. 解耦版子电路：将输入(in)与输出(out)引脚分离 ***
.subckt SRAM_9T_CELL_DECOUPLED VDD VSS BL WL WWLA WWLB Q_in QB_in Q_out QB_out
* --- 左侧支路 ---
MPUL1 net_pul1 QB_in  VDD VDD PMOS_VTG l=50n w=90n
MPUL2 Q_out    WWLA   net_pul1 VDD PMOS_VTG l=50n w=90n
MPDL1 Q_out    WWLB   net_pdl1 VSS NMOS_VTG l=50n w=180n
MPDL2 net_pdl1 QB_in  VSS VSS NMOS_VTG l=50n w=180n
MPG   Q_out WL BL VSS NMOS_VTG l=50n w=135n

* --- 右侧支路 ---
MPUR  QB_out Q_in VDD VDD PMOS_VTG l=50n w=90n
MPDR1 QB_out Q_in VX VSS NMOS_VTG l=50n w=180n
MPDR2 VX     Q_in VSS VSS NMOS_VTG l=50n w=180n
MNF   VX QB_out WWLB VSS NMOS_VTG l=50n w=90n
.ends

*** 2. 读取偏置设置 (Read Bias) ***
VVDD VDD 0 0.6
VVSS VSS 0 0
VWL  WL7 0 0.6   ; 开启字线进行读取
VBL  BL3 0 0.6   ; 位线预充高
VWWLA WWLA 0 0   ; PUL2 导通
VWWLB WWLB 0 0.6 ; PDL1 导通, NF 源极接高

*** 3. 扫描电压源 ***
VSWEEP V_IN 0 0

*** 4. 实例化：一个扫 Q，一个扫 QB ***
* 曲线 A (Normal VTC): 输入接 QB_in, 观察 Q_out
XA VDD VSS BL3 WL7 WWLA WWLB dummy1 V_IN Q_VTC_A dummy2 SRAM_9T_CELL_DECOUPLED

* 曲线 B (Mirrored VTC): 输入接 Q_in, 观察 QB_out
XB VDD VSS BL3 WL7 WWLA WWLB V_IN dummy3 dummy4 QB_VTC_B SRAM_9T_CELL_DECOUPLED

*** 5. 仿真指令 ***
.DC VSWEEP 0 0.6 0.005
.PRINT DC V(V_IN) V(Q_VTC_A) V(QB_VTC_B)
.END
