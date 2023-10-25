from elastemp_pd.core.makefiles import make_incar_static, make_kpoints
import glob, os, warnings, sys, shutil
from pymatgen.core import Structure
import pandas as pd
import os.path as osp


class make_zero_enthalpy:
    def __init__(self, root_dir, kptdensity=6000, p_min = 0, p_max = 0, num_p= 0):
        self.root_dir = root_dir
        self.kptdensity = kptdensity
        self.filelist = []
        self.indices = []
        self.p_min = p_min
        self.p_max = p_max
        self.num_p = num_p
        self.check_input_files()
        self.make_folders()


    def check_input_files(self):
        if not os.path.exists('POTCAR'):
            warnings.warn("Unable to read POTCAR file. It is either missing or corrupted. Program will stop")
            sys.exit()
            
        for fname in glob.glob(self.root_dir+'/*'):
            try:
                index = fname.split('POSCAR-')[1]
                self.indices.append(index)
               
            except:
                warnings.warn('Unable to parse file. Please ensure filename is as POSCAR-*. Program will stop.')
                sys.exit()
                
        if self.num_p==0:
            print('Number of pressure points found to be zero')
        else:
            if self.p_min>=self.p_max:
                warnings.warn("P_min is either less than or equal to P_max. Cannot set pressure calculations")
                sys.exit()
        self.pressures = [int(self.p_min + (self.p_max-self.p_min)*i/self.num_p) for i in range(0,self.num_p+1)]
        
        if not os.path.exists('output'):
            os.mkdir('output')
            
        if not os.path.exists('output/preprocessing'):
            os.mkdir('output/preprocessing')    
        
        f = open('output/preprocessing/input_parameters.txt','w')
        f.write('P_min : {} GPa\n'.format(self.p_min))
        f.write('P_max : {} GPa\n'.format(self.p_max))
        f.write('number of pressure points : {}\n'.format(self.num_p))
        f.close()
        
        df = pd.DataFrame(self.pressures)
        df.to_csv('output/preprocessing/pressures.csv',header=None,index=False)
        
        df = pd.DataFrame(self.indices)
        df.to_csv('output/preprocessing/structures.csv',header=None,index=False)

           

    def make_folders(self):
        if not os.path.exists('Calcs'):
            os.mkdir(os.getcwd()+'/Calcs')
        for index in self.indices:
            print('Making input files and folder for structure with POSCAR id {}'.format(index))
            os.mkdir(os.getcwd()+'/Calcs/Structure-{}'.format(index))
            poscar = self.root_dir+'/POSCAR-{}'.format(index)
            struct = Structure.from_file(poscar)
           
            for p in self.pressures:
                dir_name = 'Calcs/Structure-{}/P-{}'.format(index,p)
                os.mkdir(dir_name)
                self.filelist.append(dir_name)
                shutil.copy(self.root_dir+'/POSCAR-{}'.format(index),os.getcwd()+'/Calcs/Structure-{}/P-{}/POSCAR'.format(index,p))
                shutil.copy(os.getcwd()+'/POTCAR',os.getcwd()+'/Calcs/Structure-{}/P-{}/POTCAR'.format(index,p))
                struct = Structure.from_file(poscar)
                make_kpoints(struct, self.kptdensity, file_loc=os.getcwd()+"/Calcs/Structure-{}/P-{}".format(index,p))
                make_incar_static(p, file_loc=os.getcwd()+"/Calcs/Structure-{}/P-{}".format(index,p))
        
        df = pd.DataFrame(self.filelist)
        df.to_csv('output/preprocessing/filelist_enthalpy.csv',header=None,index=False)




class get_zero_enthalpy:
    def __init__(self):
        self.filelist = []
        self.check_input_files()
        self.get_energies()
          
    def check_input_files(self):
        root_dir = osp.join(os.getcwd(),'output/preprocessing')
        if not os.path.exists(root_dir+'/filelist_enthalpy.csv'):
            warnings.warn('Unable to read list of files to parse in filelist_enthalpy.csv. Please check output/preprocessing if file is missing!')
        df = pd.read_csv(root_dir+'/filelist_enthalpy.csv',header=None)
        self.filelist.append(df.iloc[:,0].values)

    def get_energies(self):
        self.filelist = self.filelist[0]
        for f in self.filelist:  
            self.get_energy_structure_pressure(f)
            
                
    def get_energy_structure_pressure(self,f):
        try:
            fil = osp.join(f,'OSZICAR')
            struct = Structure.from_file('{}/POSCAR'.format(f))
            natoms = len(struct.sites) 
            g = open(fil,'r')             
            l = [line for line in g]
            if l[-1].find('F= ')==-1:
                warnings.warn("{} not converged".format(f))
                warnings.warn("Adding arbitrarily high value of enthalpy. Rerun the calculation!")
                
                tot_energy = 1e4
            else:
                energy = float(l[-1].split()[2])
                zpe = energy/natoms
                f1 = open('{}/ZPE.txt'.format(f),'w')
                f1.write(str(zpe))
                f1.close()          
                print('Calculation of energy in folder {} successful. Please check ZPE.txt for zero point enthalpy'.format(f))
        except:
            warnings.warn("Unable to parse file {}.File is either missing or corrupted. Please check!".format(f))
        
           









