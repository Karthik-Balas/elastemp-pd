import numpy as np, sys,os
from pymatgen.core import Structure
import numpy.linalg as linalg


def make_incar_static(p, file_loc):
    """ Generates a INCAR file for static calculations if absent
    :param None
    :returns INCAR file
    :rtype plaintext file
    """
    f = open(file_loc+'/INCAR','w')
    pval = p*10
    f.write('PREC = Accurate\nICHARG=0\nNWRITE=0\nLORBIT=11\nEDIFF = 1e-6\nIBRION=2\nISIF=3\nISMEAR=-5\nISPIN=2\nEDIFFG=1e-4\n')
    f.write('ISYM=2\nLCHARG=.FALSE.\nLWAVE=.FLASE.\nNPAR=4\nSYMPREC=1e-4\nNSW=100\nSIGMA=0.01\nPOTIM=0.015\nPSTRESS={}\n'.format(pval))
    f.close()

    
def make_incar_dynamic(p, file_loc):
    """ Generates a INCAR file for static calculations if absent
    :param None
    :returns INCAR file
    :rtype plaintext file
    """
    f = open(file_loc+'/INCAR','w')
    pval = p*10
    f.write('PREC = ACCURATE\nALGO=FAST\nICHARG=0\nNWRITE=0\nLORBIT=11\nLREAL=.FALSE.\nADDGRID=.TRUE.\nEDIFF = 1e-6\nIBRION=8\nISIF=3\nISMEAR=-5\nISPIN=2\nEDIFFG=1e-4\n')
    f.write('ISYM=2\nLCHARG=.FALSE.\nLWAVE=.FLASE.\nSYMPREC=1e-4\nSIGMA=0.01\nPOTIM=0.015\nPSTRESS={}\n'.format(pval))
    f.close()

def make_kpoints(struct,kptdensity, file_loc=os.getcwd()):
    
    num_sites = struct.num_sites
    nkpts = kptdensity / num_sites
    rec_cell = 2 * np.pi * np.transpose(struct.lattice.inv_matrix)
    b1 = np.sqrt(np.dot(rec_cell[0], rec_cell[0]))
    b2 = np.sqrt(np.dot(rec_cell[1], rec_cell[1]))
    b3 = np.sqrt(np.dot(rec_cell[2], rec_cell[2]))

    step = (b1 * b2 * b3 / nkpts) ** (1. / 3)

    n1 = int(round(b1 / step))
    if np.mod(n1, 2) != 0:
        n1 = n1 - 1
        n2 = int(round(b2 / step))

    n2 = int(round(b2 / step))
    if np.mod(n2, 2) != 0:
        n2 = n2 - 1
        n3 = int(round(b3 / step))

    n3 = int(round(b3 / step))
    if np.mod(n3, 2) != 0:
        n3 = n3 - 1

    if n1 == 0:
        n1 = 1
    if n2 == 0:
        n2 = 1
    if n3 == 0:
        n3 = 1

    kpt_string = "kpt_density=%2i\n0\nGamma\n%2i %2i %2i\n 0. 0. 0.\n" % (kptdensity, n1, n2, n3)
    
    with open(file_loc+'/KPOINTS', 'w') as f:
        f.write(kpt_string)

        


