"""
Elastemp_pd is a workflow to compute metastable phase diagrams at different intervals of dG from the ground state. 
Authors : Karthik Balasubramanian, Srilok Srinivasan
"""
from elastemp_pd.enthalpy.enthalpy_calc import make_zero_enthalpy, get_zero_enthalpy
from elastemp_pd.dynamic.dynamic_calc import make_phonon
from elastemp_pd.dynamic.dynamic_calc import get_phonon
from elastemp_pd.thermal.thermal_calc import get_thermal
from elastemp_pd.thermal.metastable import get_metastable
import os

if __name__=='__main__':
    #make_zero_enthalpy(root_dir = 'POSCARS', kptdensity=6000, p_min = 0, p_max = 100, num_p=4)
    #get_zero_enthalpy()
    #make_phonon(dim=[2,2,2], kptdensity=500)
    #get_phonon()
    #get_thermal(dim=[2,2,2], t_min=0, t_max = 1000, t_step=10, make_plots=True)
    get_metastable(g_min=0,g_max=0.2,num_g=10)
