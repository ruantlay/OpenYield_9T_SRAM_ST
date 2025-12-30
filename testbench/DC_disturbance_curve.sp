* =========================================
* ST 9T SRAM Read SNM (Fig.5 equivalent)
* Xyce / HSPICE compatible
* =========================================

.include "/home/zhz/anaconda3/OpenYield_9T_SRAM_ST/sim/9T_sim/tmp_mc.spice"

.temp 25

*********************************
* 1. Bias
*********************************
VVDD  VDD  0  0.6
VVSS  VSS  0  0
VWL   WL   0  0.6
VBL   BL   0  0.6
VWWLA WWLA 0  0
VWWLB WWLB 0  0.6

*********************************
* 2. Noise source (swept)
*********************************
VNOISE NQ NQB 0

*********************************
* 3. SRAM cell (fully coupled)
*********************************
.subckt SRAM_9T_CELL VDD VSS BL WL WWLA WWLB Q QB

* --- Left branch ---
MPUL1 net_pul1 QB  VDD VDD PMOS_VTG l=50n w=90n
MPUL2 Q        WWLA net_pul1 VDD PMOS_VTG l=50n w=90n
MPDL1 Q        WWLB net_pdl1 VSS NMOS_VTG l=50n w=180n
MPDL2 net_pdl1 QB  VSS VSS NMOS_VTG l=50n w=180n
MPG   Q WL BL VSS NMOS_VTG l=50n w=135n

* --- Right branch ---
MPUR  QB Q VDD VDD PMOS_VTG l=50n w=90n
MPDR1 QB Q VX  VSS NMOS_VTG l=50n w=180n
MPDR2 VX Q VSS VSS NMOS_VTG l=50n w=180n
MNF   VX QB WWLB VSS NMOS_VTG l=50n w=90n

.ends

*********************************
* 4. Weak tie to preserve DC path
*********************************
RKEEP_Q  Q  NQ  1e9
RKEEP_QB QB NQB 1e9

*********************************
* 5. Instance
*********************************
XSRAM VDD VSS BL WL WWLA WWLB NQ NQB SRAM_9T_CELL

*********************************
* 6. DC sweep
*********************************
.DC VNOISE -0.3 0.3 0.002
.PRINT DC V(NQ) V(NQB)

.END
