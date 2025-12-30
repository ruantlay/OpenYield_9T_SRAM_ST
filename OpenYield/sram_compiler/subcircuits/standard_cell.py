# standard_cells.py
from PySpice.Spice.Netlist import SubCircuitFactory, SubCircuit
from PySpice.Unit import u_Ohm, u_pF
from .base_subcircuit import BaseSubcircuit


class PINV(BaseSubcircuit):
    """
    Standard CMOS inverter
    Used for decoder / wordline / buffer by scaling drive_factor
    """
    NAME = "PINV"
    NODES = ('VDD', 'VSS', 'A', 'Z')

    def __init__(
        self,
        nmos_model_name,
        pmos_model_name,
        base_pmos_width=0.27e-6,
        base_nmos_width=0.09e-6,
        length=0.05e-6,
        *,
        drive_factor=1.0,
        sweep=False,
        w_rc=False,
        pi_res=100 @ u_Ohm,
        pi_cap=0.001 @ u_pF,
        required_columns=None,
        pmos_model_choices=('PMOS_VTG',),
        nmos_model_choices=('NMOS_VTG',),
    ):
        super().__init__(
            nmos_model_name,
            pmos_model_name,
            base_nmos_width,
            base_pmos_width,
            length,
            w_rc=w_rc,
            pi_res=pi_res,
            pi_cap=pi_cap,
        )

        self.drive_factor = drive_factor
        self.sweep = sweep
        self.pmos_model_choices = pmos_model_choices
        self.nmos_model_choices = nmos_model_choices

        if required_columns:
            self.mos_model_index = self.read_mos_model_from_param_file(required_columns)

        self.add_transistors()

    def add_transistors(self):
        wp = self.base_pmos_width * self.drive_factor
        wn = self.base_nmos_width * self.drive_factor

        pmos_model = (
            self.pmos_pdk_model if not self.sweep
            else self.pmos_model_choices[int(self.mos_model_index['pmos'])]
        )
        nmos_model = (
            self.nmos_pdk_model if not self.sweep
            else self.nmos_model_choices[int(self.mos_model_index['nmos'])]
        )

        self.M(
            'mp', 'Z', 'A', 'VDD', 'VDD',
            model=pmos_model,
            w=wp if not self.sweep else 'pmos_width',
            l=self.length if not self.sweep else 'length'
        )
        self.M(
            'mn', 'Z', 'A', 'VSS', 'VSS',
            model=nmos_model,
            w=wn if not self.sweep else 'nmos_width',
            l=self.length if not self.sweep else 'length'
        )


class PNAND2(BaseSubcircuit):
    """
    Standard CMOS NAND2
    """
    NAME = "PNAND2"
    NODES = ('VDD', 'VSS', 'A', 'B', 'Z')

    def __init__(
        self,
        nmos_model_name,
        pmos_model_name,
        base_pmos_width=0.27e-6,
        base_nmos_width=0.18e-6,
        length=0.05e-6,
        *,
        drive_factor=1.0,
        sweep=False,
        w_rc=False,
        pi_res=100 @ u_Ohm,
        pi_cap=0.001 @ u_pF,
        required_columns=None,
        pmos_model_choices=('PMOS_VTG',),
        nmos_model_choices=('NMOS_VTG',),
    ):
        super().__init__(
            nmos_model_name,
            pmos_model_name,
            base_nmos_width,
            base_pmos_width,
            length,
            w_rc=w_rc,
            pi_res=pi_res,
            pi_cap=pi_cap,
        )

        self.drive_factor = drive_factor
        self.sweep = sweep
        self.pmos_model_choices = pmos_model_choices
        self.nmos_model_choices = nmos_model_choices

        if required_columns:
            self.mos_model_index = self.read_mos_model_from_param_file(required_columns)

        self.add_transistors()

    def add_transistors(self):
        wp = self.base_pmos_width * self.drive_factor
        wn = self.base_nmos_width * self.drive_factor

        pmos_model = (
            self.pmos_pdk_model if not self.sweep
            else self.pmos_model_choices[int(self.mos_model_index['pmos'])]
        )
        nmos_model = (
            self.nmos_pdk_model if not self.sweep
            else self.nmos_model_choices[int(self.mos_model_index['nmos'])]
        )

        self.M('mp1', 'Z', 'A', 'VDD', 'VDD', model=pmos_model, w=wp, l=self.length)
        self.M('mp2', 'Z', 'B', 'VDD', 'VDD', model=pmos_model, w=wp, l=self.length)

        self.M('mn1', 'Z', 'B', 'n1', 'VSS', model=nmos_model, w=wn, l=self.length)
        self.M('mn2', 'n1', 'A', 'VSS', 'VSS', model=nmos_model, w=wn, l=self.length)
class PNAND3(PNAND2):
    NAME = "PNAND3"
    NODES = ('VDD', 'VSS', 'A', 'B', 'C', 'Z')
    
    def add_transistors(self):
        wp = self.base_pmos_width * self.drive_factor
        wn = self.base_nmos_width * self.drive_factor
        # PMOS 串联 3 个
        self.M('mp1', 'Z', 'A', 'VDD', 'VDD', model=self.pmos_pdk_model, w=wp, l=self.length)
        self.M('mp2', 'Z', 'B', 'VDD', 'VDD', model=self.pmos_pdk_model, w=wp, l=self.length)
        self.M('mp3', 'Z', 'C', 'VDD', 'VDD', model=self.pmos_pdk_model, w=wp, l=self.length)
        # NMOS 串联 3 个
        self.M('mn1', 'n1', 'A', 'VSS', model=self.nmos_pdk_model, w=wn, l=self.length)
        self.M('mn2', 'n2', 'B', 'n1', 'VSS', model=self.nmos_pdk_model, w=wn, l=self.length)
        self.M('mn3', 'Z', 'C', 'n2', 'VSS', model=self.nmos_pdk_model, w=wn, l=self.length)


class PBUFF(BaseSubcircuit):
    NAME = "PBUFF"
    NODES = ('VDD', 'VSS', 'A', 'Z')

    def __init__(
        self,
        nmos_model_name,
        pmos_model_name,
        base_pmos_width=0.1e-6,
        base_nmos_width=0.1e-6,
        length=0.05e-6,
        w_rc=False,
        pi_res=100 @ u_Ohm,
        pi_cap=0.001 @ u_pF,
    ):
        super().__init__(
            nmos_model_name,
            pmos_model_name,
            base_nmos_width,
            base_pmos_width,
            length,
            w_rc=w_rc,
            pi_res=pi_res,
            pi_cap=pi_cap,
        )

        self.add_transistors()

    def add_transistors(self):
        self.M('mp1', 'n1', 'A', 'VDD', 'VDD',
               model=self.pmos_pdk_model, w=self.base_pmos_width, l=self.length)
        self.M('mn1', 'n1', 'A', 'VSS', 'VSS',
               model=self.nmos_pdk_model, w=self.base_nmos_width, l=self.length)

        self.M('mp2', 'Z', 'n1', 'VDD', 'VDD',
               model=self.pmos_pdk_model, w=self.base_pmos_width, l=self.length)
        self.M('mn2', 'Z', 'n1', 'VSS', 'VSS',
               model=self.nmos_pdk_model, w=self.base_nmos_width, l=self.length)

