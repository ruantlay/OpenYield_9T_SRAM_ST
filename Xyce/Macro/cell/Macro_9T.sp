* SRAM_9T_CORE_8x4 蒙特卡洛仿真测试平台
.title SRAM_9T_CORE_8x4_MC_TB

*** 1. 包含文件与仿真环境设置 ***
.include /home/zhz/anaconda3/OpenYield/sim/20251223_144911_mc_6t/tmp_mc.spice
.TRAN 1.0000e-11 6.0000e-08                     ; 瞬态分析：步长10ps，总时长60ns
.OPTIONS OUTPUT INITIAL_INTERVAL=1.0000e-11
*.SAMPLING useExpr=true
.options samples numsamples=2                   ; 蒙特卡洛采样点数设置为2


*** 2. 信号观测与打印 (修正 Xyce 路径报错版) ***

* --- A. 内部存储与反馈节点 ---
* 使用引出的扁平化节点名 Q7_3, QB7_3, VX7_3
.PRINT TRAN V(Q7_3) V(QB7_3) V(VX7_3)

* --- B. 控制信号与辅助脉冲 ---
.PRINT TRAN V(WL7) V(WWLA) V(WWLB) V(SEL0) V(SEL1)

* --- C. 位线与感测输出 ---
.PRINT TRAN V(BL3) V(SA_IN1) V(SAE) V(SA_Q1) V(SA_QB1)

* --- D. 打印与结果记录 ---
* ！！！关键修正：删掉 XSRAM_CORE.XSRAM_9T_CELL_7_3.Q 这种路径 ！！！
.print TRAN V(Q7_3) V(BL3) V(SA_Q1)



*** 3. SRAM 核心电路定义 ***
* 找到这一行，并在末尾加上 Q7_3 QB7_3 VX7_3显式加上你要引出的观测节点。
.subckt SRAM_9T_CORE_8x4 VDD VSS BL0 BL1 BL2 BL3 WL0 WL1 WL2 WL3 WL4 WL5 WL6 WL7 WWLA WWLB Q7_3 QB7_3 VX7_3
*** 基于9T SRAM 单元定义 (带寄生建模) ***
* 将 Q 和 QB 加入端口列表，这样外部层级才能通过 .Q 访问
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
*** 调整后的 8x4 SRAM 阵列实例化 ***
* 注意：删除了原有的 BLB 连接，新增了 WWLA 和 WWLB 控制线
*** 修正后的 8x4 SRAM 阵列实例化 (解决短路与层级访问问题) ***

* --- Row 0 ---
XSRAM_9T_CELL_0_0 VDD VSS BL0 WL0 WWLA WWLB Q0_0 QB0_0 VX0_0 SRAM_9T_CELL
XSRAM_9T_CELL_0_1 VDD VSS BL1 WL0 WWLA WWLB Q0_1 QB0_1 VX0_1 SRAM_9T_CELL
XSRAM_9T_CELL_0_2 VDD VSS BL2 WL0 WWLA WWLB Q0_2 QB0_2 VX0_2 SRAM_9T_CELL
XSRAM_9T_CELL_0_3 VDD VSS BL3 WL0 WWLA WWLB Q0_3 QB0_3 VX0_3 SRAM_9T_CELL

* --- Row 1 ---
XSRAM_9T_CELL_1_0 VDD VSS BL0 WL1 WWLA WWLB Q1_0 QB1_0 VX1_0 SRAM_9T_CELL
XSRAM_9T_CELL_1_1 VDD VSS BL1 WL1 WWLA WWLB Q1_1 QB1_1 VX1_1 SRAM_9T_CELL
XSRAM_9T_CELL_1_2 VDD VSS BL2 WL1 WWLA WWLB Q1_2 QB1_2 VX1_2 SRAM_9T_CELL
XSRAM_9T_CELL_1_3 VDD VSS BL3 WL1 WWLA WWLB Q1_3 QB1_3 VX1_3 SRAM_9T_CELL

* --- Row 2 ---
XSRAM_9T_CELL_2_0 VDD VSS BL0 WL2 WWLA WWLB Q2_0 QB2_0 VX2_0 SRAM_9T_CELL
XSRAM_9T_CELL_2_1 VDD VSS BL1 WL2 WWLA WWLB Q2_1 QB2_1 VX2_1 SRAM_9T_CELL
XSRAM_9T_CELL_2_2 VDD VSS BL2 WL2 WWLA WWLB Q2_2 QB2_2 VX2_2 SRAM_9T_CELL
XSRAM_9T_CELL_2_3 VDD VSS BL3 WL2 WWLA WWLB Q2_3 QB2_3 VX2_3 SRAM_9T_CELL

* --- Row 3 ---
XSRAM_9T_CELL_3_0 VDD VSS BL0 WL3 WWLA WWLB Q3_0 QB3_0 VX3_0 SRAM_9T_CELL
XSRAM_9T_CELL_3_1 VDD VSS BL1 WL3 WWLA WWLB Q3_1 QB3_1 VX3_1 SRAM_9T_CELL
XSRAM_9T_CELL_3_2 VDD VSS BL2 WL3 WWLA WWLB Q3_2 QB3_2 VX3_2 SRAM_9T_CELL
XSRAM_9T_CELL_3_3 VDD VSS BL3 WL3 WWLA WWLB Q3_3 QB3_3 VX3_3 SRAM_9T_CELL

* --- Row 4 ---
XSRAM_9T_CELL_4_0 VDD VSS BL0 WL4 WWLA WWLB Q4_0 QB4_0 VX4_0 SRAM_9T_CELL
XSRAM_9T_CELL_4_1 VDD VSS BL1 WL4 WWLA WWLB Q4_1 QB4_1 VX4_1 SRAM_9T_CELL
XSRAM_9T_CELL_4_2 VDD VSS BL2 WL4 WWLA WWLB Q4_2 QB4_2 VX4_2 SRAM_9T_CELL
XSRAM_9T_CELL_4_3 VDD VSS BL3 WL4 WWLA WWLB Q4_3 QB4_3 VX4_3 SRAM_9T_CELL

* --- Row 5 ---
XSRAM_9T_CELL_5_0 VDD VSS BL0 WL5 WWLA WWLB Q5_0 QB5_0 VX5_0 SRAM_9T_CELL
XSRAM_9T_CELL_5_1 VDD VSS BL1 WL5 WWLA WWLB Q5_1 QB5_1 VX5_1 SRAM_9T_CELL
XSRAM_9T_CELL_5_2 VDD VSS BL2 WL5 WWLA WWLB Q5_2 QB5_2 VX5_2 SRAM_9T_CELL
XSRAM_9T_CELL_5_3 VDD VSS BL3 WL5 WWLA WWLB Q5_3 QB5_3 VX5_3 SRAM_9T_CELL

* --- Row 6 ---
XSRAM_9T_CELL_6_0 VDD VSS BL0 WL6 WWLA WWLB Q6_0 QB6_0 VX6_0 SRAM_9T_CELL
XSRAM_9T_CELL_6_1 VDD VSS BL1 WL6 WWLA WWLB Q6_1 QB6_1 VX6_1 SRAM_9T_CELL
XSRAM_9T_CELL_6_2 VDD VSS BL2 WL6 WWLA WWLB Q6_2 QB6_2 VX6_2 SRAM_9T_CELL
XSRAM_9T_CELL_6_3 VDD VSS BL3 WL6 WWLA WWLB Q6_3 QB6_3 VX6_3 SRAM_9T_CELL

* --- Row 7 (Target Row) ---
XSRAM_9T_CELL_7_0 VDD VSS BL0 WL7 WWLA WWLB Q7_0 QB7_0 VX7_0 SRAM_9T_CELL
XSRAM_9T_CELL_7_1 VDD VSS BL1 WL7 WWLA WWLB Q7_1 QB7_1 VX7_1 SRAM_9T_CELL
XSRAM_9T_CELL_7_2 VDD VSS BL2 WL7 WWLA WWLB Q7_2 QB7_2 VX7_2 SRAM_9T_CELL
XSRAM_9T_CELL_7_3 VDD VSS BL3 WL7 WWLA WWLB Q7_3 QB7_3 VX7_3 SRAM_9T_CELL
.ends SRAM_9T_CORE_8x4
*** 4. 外围逻辑电路定义 (译码器/驱动器/预充/MUX/SA) ***
* 3-8 行译码器：将 3位地址(A0-A2)转换为 8根字线选择信号
    * 包含反相器、AND3(地址组合)和AND2(使能控制)
.subckt DECODER_CASCADE VDD VSS A0 A1 A2 WL0 WL1 WL2 WL3 WL4 WL5 WL6 WL7
.subckt DECODER3_8 VDD VSS EN A0 A1 A2 WL0 WL1 WL2 WL3 WL4 WL5 WL6 WL7
.subckt PINV VDD VSS A Z
Mpinv_pmos Z A VDD VDD PMOS_VTG l=5e-08 w=2.7e-07
Mpinv_nmos Z A VSS VSS NMOS_VTG l=5e-08 w=9e-08
.ends PINV

.subckt AND3 VDD VSS A B C Z
.subckt PNAND3 VDD VSS A B C Z
Mpnand3_pmos1 Z A VDD VDD PMOS_VTG l=5e-08 w=2.7e-07
Mpnand3_pmos2 Z B VDD VDD PMOS_VTG l=5e-08 w=2.7e-07
Mpnand3_pmos3 Z C VDD VDD PMOS_VTG l=5e-08 w=2.7e-07
Mpnand3_nmos1 Z A net1_nand VSS NMOS_VTG l=5e-08 w=1.8e-07
Mpnand3_nmos2 net1_nand B net2_nand VSS NMOS_VTG l=5e-08 w=1.8e-07
Mpnand3_nmos3 net2_nand C VSS VSS NMOS_VTG l=5e-08 w=1.8e-07
.ends PNAND3

.subckt PINV VDD VSS A Z
Mpinv_pmos Z A VDD VDD PMOS_VTG l=5e-08 w=2.7e-07
Mpinv_nmos Z A VSS VSS NMOS_VTG l=5e-08 w=9e-08
.ends PINV
RR_A_0 A A_seg0 100Ohm
CCg_A_0 A_seg0 0 0.001pF
RR_A_1 A_seg0 A_end 100Ohm
CCg_A_1 A_end 0 0.001pF
RR_B_0 B B_seg0 100Ohm
CCg_B_0 B_seg0 0 0.001pF
RR_B_1 B_seg0 B_end 100Ohm
CCg_B_1 B_end 0 0.001pF
RR_C_0 C C_seg0 100Ohm
CCg_C_0 C_seg0 0 0.001pF
RR_C_1 C_seg0 C_end 100Ohm
CCg_C_1 C_end 0 0.001pF
RR_zb_int_0 zb_int zb_int_seg0 100Ohm
CCg_zb_int_0 zb_int_seg0 0 0.001pF
RR_zb_int_1 zb_int_seg0 zb_int_end 100Ohm
CCg_zb_int_1 zb_int_end 0 0.001pF
RR_Z_0 Z Z_seg0 100Ohm
CCg_Z_0 Z_seg0 0 0.001pF
RR_Z_1 Z_seg0 Z_end 100Ohm
CCg_Z_1 Z_end 0 0.001pF
XPNAND3 VDD VSS A_end B_end C_end zb_int_end PNAND3
XPINV VDD VSS zb_int_end Z_end PINV
.ends AND3

.subckt AND2 VDD VSS A B Z
.subckt PNAND2 VDD VSS A B Z
Mpnand2_pmos1 Z A VDD VDD PMOS_VTG l=5e-08 w=2.7e-07
Mpnand2_pmos2 Z B VDD VDD PMOS_VTG l=5e-08 w=2.7e-07
Mpnand2_nmos1 Z B net1_nand VSS NMOS_VTG l=5e-08 w=1.8e-07
Mpnand2_nmos2 net1_nand A VSS VSS NMOS_VTG l=5e-08 w=1.8e-07
.ends PNAND2

.subckt PINV VDD VSS A Z
Mpinv_pmos Z A VDD VDD PMOS_VTG l=5e-08 w=2.7e-07
Mpinv_nmos Z A VSS VSS NMOS_VTG l=5e-08 w=9e-08
.ends PINV
RR_A_0 A A_seg0 100Ohm
CCg_A_0 A_seg0 0 0.001pF
RR_A_1 A_seg0 A_end 100Ohm
CCg_A_1 A_end 0 0.001pF
RR_B_0 B B_seg0 100Ohm
CCg_B_0 B_seg0 0 0.001pF
RR_B_1 B_seg0 B_end 100Ohm
CCg_B_1 B_end 0 0.001pF
RR_zb_int_0 zb_int zb_int_seg0 100Ohm
CCg_zb_int_0 zb_int_seg0 0 0.001pF
RR_zb_int_1 zb_int_seg0 zb_int_end 100Ohm
CCg_zb_int_1 zb_int_end 0 0.001pF
RR_Z_0 Z Z_seg0 100Ohm
CCg_Z_0 Z_seg0 0 0.001pF
RR_Z_1 Z_seg0 Z_end 100Ohm
CCg_Z_1 Z_end 0 0.001pF
XPNAND3 VDD VSS A_end B_end zb_int_end PNAND2
XPINV VDD VSS zb_int_end Z_end PINV
.ends AND2
XINV_A1 VDD VSS A0 A0b PINV
XINV_A2 VDD VSS A1 A1b PINV
XINV_A3 VDD VSS A2 A2b PINV
XAND0 VDD VSS A0b A1b A2b WL0_pre AND3
XAND_EN0 VDD VSS WL0_pre EN WL0 AND2
XAND1 VDD VSS A0b A1b A2 WL1_pre AND3
XAND_EN1 VDD VSS WL1_pre EN WL1 AND2
XAND2 VDD VSS A0b A1 A2b WL2_pre AND3
XAND_EN2 VDD VSS WL2_pre EN WL2 AND2
XAND3 VDD VSS A0b A1 A2 WL3_pre AND3
XAND_EN3 VDD VSS WL3_pre EN WL3 AND2
XAND4 VDD VSS A0 A1b A2b WL4_pre AND3
XAND_EN4 VDD VSS WL4_pre EN WL4 AND2
XAND5 VDD VSS A0 A1b A2 WL5_pre AND3
XAND_EN5 VDD VSS WL5_pre EN WL5 AND2
XAND6 VDD VSS A0 A1 A2b WL6_pre AND3
XAND_EN6 VDD VSS WL6_pre EN WL6 AND2
XAND7 VDD VSS A0 A1 A2 WL7_pre AND3
XAND_EN7 VDD VSS WL7_pre EN WL7 AND2
.ends DECODER3_8
XDEC_0_0 VDD VSS VDD A2 A1 A0 WL0 WL1 WL2 WL3 WL4 WL5 WL6 WL7 DECODER3_8
.ends DECODER_CASCADE
*** @@@@@@@@@@@@@@@@@@@@@@@针对 9T 拓扑优化的字线驱动器 ***
.subckt WORDLINEDRIVER VDD VSS A B Z Z_WWLA Z_WWLB
* A. 来自译码器的选通信号 (Active High)
* B. 全局字线使能信号 WL_EN (Active High)
* Z. 输出到存储单元的 WL
* Z_WWLA/B. 输出到存储单元的辅助控制信号

*** 1. 内部逻辑门定义 ***
.subckt PNAND2 VDD VSS A B Z
Mpnand2_pmos1 Z A VDD VDD PMOS_VTG l=5e-08 w=2.7e-07
Mpnand2_pmos2 Z B VDD VDD PMOS_VTG l=5e-08 w=2.7e-07
Mpnand2_nmos1 Z B net1_nand VSS NMOS_VTG l=5e-08 w=1.8e-07
Mpnand2_nmos2 net1_nand A VSS VSS NMOS_VTG l=5e-08 w=1.8e-07
.ends PNAND2

.subckt PINV VDD VSS A Z
Mpinv_pmos Z A VDD VDD PMOS_VTG l=5e-08 w=2.7e-07
Mpinv_nmos Z A VSS VSS NMOS_VTG l=5e-08 w=9e-08
.ends PINV

*** 2. RC 寄生建模 (输入端) ***
RR_A_0 A A_seg0 100Ohm
CCg_A_0 A_seg0 0 0.001pF
RR_A_1 A_seg0 A_end 100Ohm
CCg_A_1 A_end 0 0.001pF

RR_B_0 B B_seg0 100Ohm
CCg_B_0 B_seg0 0 0.001pF
RR_B_1 B_seg0 B_end 100Ohm
CCg_B_1 B_end 0 0.001pF

*** 3. 核心驱动逻辑 ***
* 生成主选通信号 (NAND + INV = AND)
XPNAND2 VDD VSS A_end B_end zb_int PNAND2
XPINV_WL VDD VSS zb_int Z PINV

* 生成辅助控制信号 (根据需要可以调整极性)
* 这里假设 WWLA 和 WWLB 在字线选通时同步变为高电平 (1.0V)
XPINV_WWLA VDD VSS zb_int Z_WWLA PINV
XPINV_WWLB VDD VSS zb_int Z_WWLB PINV

.ends WORDLINEDRIVER

*** @@@@@@@@@@@@@@@@@@@@@@@调整后的单端预充电电路 (仅针对 BL) ***
.subckt PRECHARGE VDD ENB BL
* ENB 为低电平时，将位线 BL 预充至 VDD

* --- 寄生 RC 建模 ---
RR_BL_0    BL      BL_seg0   100Ohm
CCg_BL_0   BL_seg0 0         0.001pF
RR_BL_1    BL_seg0 BL_end    100Ohm
CCg_BL_1   BL_end  0         0.001pF

RR_ENB_0   ENB     ENB_end   100Ohm
CCg_ENB_0  ENB_end 0         0.001pF

* --- 预充逻辑 ---
* 只保留 M1 用于将 BL 上拉到 VDD
M1 BL_end ENB_end VDD VDD PMOS_VTG l=5e-08 w=1.35e-07

* 注意：由于是单端结构，原有的 M2 (BLB上拉) 和 M3 (平衡管) 已移除
.ends PRECHARGE

*** @@@@@@@@@@@@@@@@@@@@@@@针对单端 9T 拓扑优化的列选择开关 (2选1) ***
.subckt COLUMNMUX2 VDD VSS SA_IN SEL0 SEL1 BL0 BL1
* SA_IN. 连接到灵敏放大器的输入端
* SEL0/1. 列选择使能信号
* BL0/1. 来自存储阵列的单端位线

* --- SEL0 通路逻辑与寄生建模 ---
RR_SEL0_0   SEL0       SEL0_end   100Ohm
CCg_SEL0_0  SEL0_end   0          0.001pF
RR_SELB0_0  SELB0      SELB0_end  100Ohm
CCg_SELB0_0 SELB0_end  0          0.001pF

* 生成互补选择信号 SELB0 (用于传输门控制)
MInvp_0 SELB0_end SEL0_end VDD VDD PMOS_VTG l=5e-08 w=1.35e-07
MInvn_0 SELB0_end SEL0_end VSS VSS NMOS_VTG l=5e-08 w=1.35e-07

* BL0 传输门 (Transmission Gate). 当 SEL0 为高时接通
MMuxn_BL_0 BL0 SEL0_end  SA_IN VSS NMOS_VTG l=5e-08 w=1.35e-07
MMuxp_BL_0 BL0 SELB0_end SA_IN VDD PMOS_VTG l=5e-08 w=1.35e-07

* --- SEL1 通路逻辑与寄生建模 ---
RR_SEL1_0   SEL1       SEL1_end   100Ohm
CCg_SEL1_0  SEL1_end   0          0.001pF
RR_SELB1_0  SELB1      SELB1_end  100Ohm
CCg_SELB1_0 SELB1_end  0          0.001pF

* 生成互补选择信号 SELB1
MInvp_1 SELB1_end SEL1_end VDD VDD PMOS_VTG l=5e-08 w=1.35e-07
MInvn_1 SELB1_end SEL1_end VSS VSS NMOS_VTG l=5e-08 w=1.35e-07

* BL1 传输门. 当 SEL1 为高时接通
MMuxn_BL_1 BL1 SEL1_end  SA_IN VSS NMOS_VTG l=5e-08 w=1.35e-07
MMuxp_BL_1 BL1 SELB1_end SA_IN VDD PMOS_VTG l=5e-08 w=1.35e-07

.ends COLUMNMUX2

*** @@@@@@@@@@@@@@@@@@@@@@@针对单端 9T 拓扑优化的灵敏放大器 (带参考端 VREF) ***
.subckt SENSEAMP VDD VSS EN IN VREF Q QB
* IN. 连接到 Column MUX 输出的单端位线信号
* VREF. 外部提供的参考基准电平 (通常为 0.8V ~ 0.9V)
* EN. 使能信号 (SAE)
* Q/QB. 锁存输出

*** 1. 寄生 RC 建模 (保持 Demo 风格) ***
RR_EN_0 EN EN_seg0 100Ohm
CCg_EN_0 EN_seg0 0 0.001pF
RR_EN_1 EN_seg0 EN_end 100Ohm
CCg_EN_1 EN_end 0 0.001pF

RR_IN_0 IN IN_seg0 100Ohm
CCg_IN_0 IN_seg0 0 0.001pF
RR_IN_1 IN_seg0 IN_end 100Ohm
CCg_IN_1 IN_end 0 0.001pF

RR_VREF_0 VREF VREF_seg0 100Ohm
CCg_VREF_0 VREF_seg0 0 0.001pF
RR_VREF_1 VREF_seg0 VREF_end 100Ohm
CCg_VREF_1 VREF_end 0 0.001pF

RR_Q_0 Q Q_seg0 100Ohm
CCg_Q_0 Q_seg0 0 0.001pF
RR_Q_1 Q_seg0 Q_end 100Ohm
CCg_Q_1 Q_end 0 0.001pF

RR_QB_0 QB QB_seg0 100Ohm
CCg_QB_0 QB_seg0 0 0.001pF
RR_QB_1 QB_seg0 QB_end 100Ohm
CCg_QB_1 QB_end 0 0.001pF

*** 2. 核心电路逻辑 (电压锁存型) ***
* 交叉耦合反相器对 (Cross-Coupled Pair)
M1 Q  QB_end net1 VSS NMOS_VTG l=5e-08 w=2.7e-07
M2 Q  QB_end VDD  VDD PMOS_VTG l=5e-08 w=5.4e-07
M3 QB Q_end  net1 VSS NMOS_VTG l=5e-08 w=2.7e-07
M4 QB Q_end  VDD  VDD PMOS_VTG l=5e-08 w=5.4e-07

* 输入与参考评估管 (改为 PMOS 输入，适合靠近 VDD 的感测)
M5 Q  EN_end IN_end   VDD PMOS_VTG l=5e-08 w=7.2e-07
M6 QB EN_end VREF_end VDD PMOS_VTG l=5e-08 w=7.2e-07

* 使能下拉管
M7 net1 EN_end VSS VSS NMOS_VTG l=5e-08 w=2.7e-07

.ends SENSEAMP

*** 5. 顶层激励与实例化 ***



*** 1. 电源与参考电压定义 ***
* 文献针对近阈值设计，建议 VDD 设为 0.6V 左右以体现 ST 单元优势
VVDD VDD VSS 0.6V
VVSS VSS 0 0V
* 单端读取参考电压：设在 VDD 附近以检测位线微小放电 (典型值 VDD-100mV)
VVREF VREF_SIG VSS 0.5V

*** 2. 核心阵列实例化 (8x4 结构) ***
* 端口顺序：VDD VSS BL WL WWLA WWLB
XSRAM_CORE VDD VSS BL0 BL1 BL2 BL3 WL0 WL1 WL2 WL3 WL4 WL5 WL6 WL7 WWLA WWLB Q7_3 QB7_3 VX7_3 SRAM_9T_CORE_8x4

*** 3. 地址与字线使能信号 (A0-A2 选中 WL7) ***
VADDR_0 A0 VSS DC 0V PULSE(0V 0.6V 4.5ns 0.1ns 0.1ns 7.5ns 60ns)
VADDR_1 A1 VSS DC 0V PULSE(0V 0.6V 4.5ns 0.1ns 0.1ns 7.5ns 60ns)
VADDR_2 A2 VSS DC 0V PULSE(0V 0.6V 4.5ns 0.1ns 0.1ns 7.5ns 60ns)
VWL_EN WL_EN VSS DC 0V PULSE(0V 0.6V 5ns 0.1ns 0.1ns 7ns 60ns)

*** 4. 文献核心：写辅助 (Write Assist) 偏置策略 ***
* 逻辑：读取/保持时 WWLA=0, WWLB=VDD；写入时根据数据翻转信号
* 模拟写入 '0' 场景：WWLA 升压以削弱上拉反馈
VWWLA WWLA VSS DC 0V PULSE(0V 0.6V 5ns 0.1ns 0.1ns 7ns 60ns)
* 模拟写入 '1' 场景：WWLB 降压以削弱下拉反馈
VWWLB WWLB VSS DC 0.6V PULSE(0.6V 0V 5ns 0.1ns 0.1ns 7ns 60ns)

*** 5. 外围模块实例化 ***
* 单端预充电 (针对 BL0-BL3)
XPRE_0 VDD PRE BL0 PRECHARGE
XPRE_1 VDD PRE BL1 PRECHARGE
XPRE_2 VDD PRE BL2 PRECHARGE
XPRE_3 VDD PRE BL3 PRECHARGE
VPRE PRE VSS DC 0.6V PULSE(0.6V 0V 0ns 0.1ns 0.1ns 4ns 60ns)

* 单端列选择开关 (2选1)
XMUX_0 VDD VSS SA_IN0 SEL0 SEL1 BL0 BL1 COLUMNMUX2
XMUX_1 VDD VSS SA_IN1 SEL0 SEL1 BL2 BL3 COLUMNMUX2
VSEL_0 SEL0 VSS 0V
VSEL_1 SEL1 VSS DC 0V PULSE(0V 0.6V 5ns 0.1ns 0.1ns 10ns 60ns)

* 单端灵敏放大器 (带参考电压 VREF)
XSA_0 VDD VSS SAE SA_IN0 VREF_SIG SA_Q0 SA_QB0 SENSEAMP
XSA_1 VDD VSS SAE SA_IN1 VREF_SIG SA_Q1 SA_QB1 SENSEAMP
VSAE SAE VSS DC 0V PULSE(0V 0.6V 12ns 0.1ns 0.1ns 6ns 60ns)

*** 6. 字线驱动器 (同步输出辅助信号) ***
XWL_DRV_7 VDD VSS DEC_WL7 WL_EN WL7 WWLA_OUT WWLB_OUT WORDLINEDRIVER

*** 6. 初始条件 (Initial Conditions) - 适配 Xyce 扁平化节点名 ***

* --- A. 位线与外围电路初始化 ---
* 单端位线初始化
.ic V(BL0)=0V V(BL1)=0V V(BL2)=0V V(BL3)=0V
* 灵敏放大器输入端初始化 (设为预充后的高电平)
.ic V(SA_IN0)=0.6V V(SA_IN1)=0.6V 

* --- B. 核心观测单元状态 (Row 7, Col 3) ---
* 模拟预存数据 '0'：Q=0V, QB=0.6V, VX 节点受反馈导通也设为 0.6V
.ic V(Q7_3)=0V 
.ic V(QB7_3)=0.6V
.ic V(VX7_3)=0.6V

* --- C. 阵列其余单元初始化 (防止不收敛) ---
* Row 0
.ic V(XSRAM_CORE.Q0_0)=0V V(XSRAM_CORE.QB0_0)=0.6V V(XSRAM_CORE.Q0_1)=0V V(XSRAM_CORE.QB0_1)=0.6V
.ic V(XSRAM_CORE.Q0_2)=0V V(XSRAM_CORE.QB0_2)=0.6V V(XSRAM_CORE.Q0_3)=0V V(XSRAM_CORE.QB0_3)=0.6V

* Row 1
.ic V(XSRAM_CORE.Q1_0)=0V V(XSRAM_CORE.QB1_0)=0.6V V(XSRAM_CORE.Q1_1)=0V V(XSRAM_CORE.QB1_1)=0.6V
.ic V(XSRAM_CORE.Q1_2)=0V V(XSRAM_CORE.QB1_2)=0.6V V(XSRAM_CORE.Q1_3)=0V V(XSRAM_CORE.QB1_3)=0.6V

* Row 2
.ic V(XSRAM_CORE.Q2_0)=0V V(XSRAM_CORE.QB2_0)=0.6V V(XSRAM_CORE.Q2_1)=0V V(XSRAM_CORE.QB2_1)=0.6V
.ic V(XSRAM_CORE.Q2_2)=0V V(XSRAM_CORE.QB2_2)=0.6V V(XSRAM_CORE.Q2_3)=0V V(XSRAM_CORE.QB2_3)=0.6V

* Row 3
.ic V(XSRAM_CORE.Q3_0)=0V V(XSRAM_CORE.QB3_0)=0.6V V(XSRAM_CORE.Q3_1)=0V V(XSRAM_CORE.QB3_1)=0.6V
.ic V(XSRAM_CORE.Q3_2)=0V V(XSRAM_CORE.QB3_2)=0.6V V(XSRAM_CORE.Q3_3)=0V V(XSRAM_CORE.QB3_3)=0.6V

* Row 4
.ic V(XSRAM_CORE.Q4_0)=0V V(XSRAM_CORE.QB4_0)=0.6V V(XSRAM_CORE.Q4_1)=0V V(XSRAM_CORE.QB4_1)=0.6V
.ic V(XSRAM_CORE.Q4_2)=0V V(XSRAM_CORE.QB4_2)=0.6V V(XSRAM_CORE.Q4_3)=0V V(XSRAM_CORE.QB4_3)=0.6V

* Row 5
.ic V(XSRAM_CORE.Q5_0)=0V V(XSRAM_CORE.QB5_0)=0.6V V(XSRAM_CORE.Q5_1)=0V V(XSRAM_CORE.QB5_1)=0.6V
.ic V(XSRAM_CORE.Q5_2)=0V V(XSRAM_CORE.QB5_2)=0.6V V(XSRAM_CORE.Q5_3)=0V V(XSRAM_CORE.QB5_3)=0.6V

* Row 6
.ic V(XSRAM_CORE.Q6_0)=0V V(XSRAM_CORE.QB6_0)=0.6V V(XSRAM_CORE.Q6_1)=0V V(XSRAM_CORE.QB6_1)=0.6V
.ic V(XSRAM_CORE.Q6_2)=0V V(XSRAM_CORE.QB6_2)=0.6V V(XSRAM_CORE.Q6_3)=0V V(XSRAM_CORE.QB6_3)=0.6V

* Row 7 (其余单元)
.ic V(XSRAM_CORE.Q7_0)=0V V(XSRAM_CORE.QB7_0)=0.6V V(XSRAM_CORE.Q7_1)=0V V(XSRAM_CORE.QB7_1)=0.6V
.ic V(XSRAM_CORE.Q7_2)=0V V(XSRAM_CORE.QB7_2)=0.6V
*** 7. 性能指标测量 (完全对齐文献逻辑) ***

* --- A. 时序与延迟测量 (Timing & Delay) ---
* 1. 预充延迟：测量 BL3 从 0V 上拉至 0.54V (VDD的90%) 的时间
.meas TRAN TPRCH TRIG V(PRE)=0.3 FALL=1 TARG V(BL3)=0.54 RISE=1

* 2. 译码与字线驱动延迟：针对 WL7 路径
.meas TRAN TDECODER TRIG V(A0)=0.3 RISE=1 TARG V(DEC_WL7)=0.3 RISE=1
.meas TRAN TWLDRV  TRIG V(DEC_WL7)=0.3 RISE=1 TARG V(WL7)=0.3 RISE=1

* 3. 关键写入延迟 (Write '1' Delay)：测量使能 WWLB 后 Q 从 0V 翻转至 0.3V 的时间
.meas TRAN TWRITE1  TRIG V(WL7)=0.3 RISE=1 TARG V(Q7_3)=0.3 RISE=1

* 4. 单端读取延迟：测量 BL3 下降到参考电压 VREF 触发 SA 输出的时间
.meas TRAN TSA_READ TRIG V(SAE)=0.3 RISE=1 TARG V(SA_Q1)=0.06 FALL=1

* --- B. 功耗测量 (Power Analysis) ---
* 5. 总体平均功耗 (全周期)
.meas TRAN PAVG AVG {V(VDD)*I(VVDD)} FROM=0.0 TO=60n

* 6. 动态读/写功耗 (活跃期)
.meas TRAN PDYN AVG {V(VDD)*I(VVDD)} FROM=4n TO=15n

* 7. 静态漏电功耗 (待机期)：利用该 9T 单元在近阈值下的超低漏电特性进行测量
.meas TRAN PLEAK AVG {V(VDD)*I(VVDD)} FROM=20n TO=60n

* --- C. 写裕量评估 (Write Margin Analysis) ---
* 8. 测量写辅助信号 WWLA 对反馈的削弱程度：观察写入 0 时节点 Q 的电压下降斜率
.meas TRAN T_FLIP0 WHEN V(Q7_3)=0.3 FALL=1

.end