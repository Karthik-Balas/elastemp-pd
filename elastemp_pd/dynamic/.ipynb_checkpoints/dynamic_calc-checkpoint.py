from elastemp_pd.core.makefiles import make_incar_dynamic, make_kpoints
import glob, os, warnings, sys, shutil
import os.path as osp
from pymatgen.core import Structure
import pandas as pd

class make_phonon:
    def __init__(self,kptdensity=1000, dim=[2,2,2]):
        self.dim = dim
        self.kptdensity = kptdensity
        self.filelist = []
        self.phonon_filelist=[]
        self.root_dir = os.getcwd()
        self.check_input_files()
        self.make_folders()
      


    def check_input_files(self):
        root_dir = osp.join(os.getcwd(),'output/preprocessing')
        if not os.path.exists(root_dir+'/filelist_enthalpy.csv'):
            warnings.warn('Unable to read list of files to parse in filelist_enthalpy.csv. Please check output/preprocessing if file is missing!')
        df = pd.read_csv(root_dir+'/filelist_enthalpy.csv',header=None)
        self.filelist.append(df.iloc[:,0].values)
       
        if not os.path.exists('INCAR_dynamic'):
            warnings.warn("Unable to read INCAR_dynamic file. A default file will be added.")
            warnings.warn("For most cases, default file is good. For best results, tailor the INCAR file in Phonon_calculations folder")
            
        
        
    def make_folders(self):
        self.filelist = self.filelist[0]
        dim0,dim1,dim2 = self.dim
       
        for f in self.filelist:  
            p = int(f.split('P-')[1])
            if not os.path.exists(f+'/Phonon_calculation'):
                os.mkdir(f+'/Phonon_calculation')
            
            if not os.path.exists(f+'/ZPE.txt'):
                warnings.warn('ZPE file does not exist in folder {}. Please check static calculation. Program will stop!'.format(f))
                sys.exit()
            
            if not os.path.exists(f+'/CONTCAR'):
                warnings.warn('CONTCAR file does not exist in folder {}. Please check static calculation. Program will stop!'.format(f))
                sys.exit()
            
            shutil.copy(f+'/ZPE.txt',f+'/Phonon_calculation/ZPE.txt')
            #shutil.copy(f+'/CONTCAR',f+'/Phonon_calculation/POSCAR')
            shutil.copy(f+'/POSCAR',f+'/Phonon_calculation/POSCAR')
            shutil.copy(f+'/POTCAR',f+'/Phonon_calculation/POTCAR')
            warnings.warn('Minor symmetry breakings in CONTCAR file can cause large phonon calculations because of calculated asymmetry. Please manually adjust POSCAR file in Phonon calculations folder')
            os.chdir(f+'/Phonon_calculation')
            self.phonon_filelist.append(os.getcwd())
            shutil.copy('POSCAR','POSCAR-unitcell')
            os.system("phonopy -d --dim='{} {} {}' -c POSCAR-unitcell".format(dim0,dim1,dim2))           
            shutil.move('SPOSCAR','POSCAR')
            struct = Structure.from_file('POSCAR')
            make_kpoints(struct, self.kptdensity, file_loc = os.getcwd())
            
            make_incar_dynamic(p, file_loc = os.getcwd())
            os.chdir(self.root_dir)
        df = pd.DataFrame(self.phonon_filelist)
        df.to_csv('output/preprocessing/filelist_dynamic.csv',header=None,index=False)

class get_phonon:
    
    def __init__(self):
        self.filelist=[]
        self.root_dir = os.getcwd()
        self.check_input_files()
        self.phonon_calculations()
        
        
    def check_input_files(self):
        root_dir = osp.join(os.getcwd(),'output/preprocessing')
        if not os.path.exists(root_dir+'/filelist_dynamic.csv'):
            warnings.warn('Unable to read list of files to parse in filelist_dynamic.csv. Please check output/preprocessing if file is missing!')
        df = pd.read_csv(root_dir+'/filelist_dynamic.csv',header=None)
        self.filelist.append(df.iloc[:,0].values)
       
    def phonon_calculations(self):
        self.filelist = self.filelist[0]
        for f in self.filelist:  
          
            if not os.path.exists(f):
                warnings.warn("Phonon_calculation folder is missing!. Program will stop.")
                sys.exit()
            
            os.chdir(f)
            print("Extracting force constants in folder {}".format(f))
            if not os.path.exists('vasprun.xml'):
                print('Vasprun.xml file is missing!. Program will stop')
                sys.exit()
            
            os.system('phonopy --fc vasprun.xml')
            os.chdir(self.root_dir)
            

    
    




