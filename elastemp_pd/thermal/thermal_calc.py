import os,yaml,numpy as np,sys, pandas as pd
import os.path as osp
import warnings
from pymatgen.core import Structure
import matplotlib.pyplot as plt


class get_thermal:
    """ 
    Phonon class consisting of functions to run phonopy phonon calculations.
    """
    def __init__(self,dim,t_min, t_max,t_step, make_plots):
        """ Constructor function for phonon_thermal class
        :param dim  : dimension of supercell
               tmax : Maximum temperature at which elastic constants calculations are run.
        """
        self.dim=dim
        self.t_min = t_min
        self.t_max = t_max
        self.t_step = t_step
        self.make_plots= make_plots
        self.root_dir = os.getcwd()
        self.filelist=[]
        self.check_input_files()
        self.get_phonon_thermal()
        self.post_processing()
    
    def check_input_files(self):
        root_dir = osp.join(os.getcwd(),'output/preprocessing')
        if not os.path.exists(root_dir+'/filelist_dynamic.csv'):
            warnings.warn('Unable to read list of files to parse in filelist_dynamic.csv. Please check output/preprocessing if file is missing!')
        df = pd.read_csv(root_dir+'/filelist_dynamic.csv',header=None)
        self.filelist.append(df.iloc[:,0].values)
        if not os.path.exists(root_dir+'/input_parameters_temp.txt'):
            f = open(root_dir+'/input_parameters_temp.txt','w')
            file_string = 'T_min = {}\n T_max = {}\n T_step = {}\n'.format(self.t_min, self.t_max, self.t_step)
            f.write(file_string)
            f.close()

    def make_mesh_conf(self):
        """ Function to create mesh file needed for phonopy calculations.
        :param None
        :returns mesh.conf  : phonopy settings file
        :rtype   mesh.conf  : plaintext file
        """
        dim1,dim2,dim3 = self.dim
        f = open('mesh.conf','w')
        mesh_string = 'DIM={} {} {}\nMP= 48 48 48\nTMIN={}\nTMAX={}\nTSTEP={}\n'.format(dim1,dim2,dim3,self.t_min, self.t_max, self.t_step)
        f.write(mesh_string)
        f.write('FORCE_CONSTANTS=READ')        


    def run_phonopy_thermal(self):
        """ Function to run thermal properties calculations via phonopy.
        """
        self.make_mesh_conf()
        os.system('phonopy -c POSCAR-unitcell -t mesh.conf')
       

    def extract_thermal_yaml(self):
        """ Function to extract thermodynamic properties from thermal_properties.yaml file.
        :param None
        :returns energy_temp file containing thermodynamic properties
        :rtype   energy_temp :dat file
        """
        fil = 'thermal_properties.yaml'
        try:
            data = yaml.load(open(fil),Loader=yaml.FullLoader)
        except:
            print('Unable to read thermal_properties file. Program will stop!')
            sys.exit()
        zpe = float(open('ZPE.txt').readlines()[0])
        
        struct = Structure.from_file('POSCAR-unitcell')
        natoms = len(struct.sites)
        df = pd.DataFrame()
        temp_array = []; energy_array = []; cv_array=[]
        data_th = data['thermal_properties']
        
        for m in range(len(data_th)):
            temp = data_th[m]['temperature']
            en1 = (data_th[m]['free_energy']*0.01)/(natoms)
            cv = (data_th[m]['heat_capacity'])/(natoms)
            en1 = en1
            en = en1+zpe
            temp_array.append(temp)
            cv_array.append(cv)
            energy_array.append(en)
        
        if self.make_plots:
            plt.figure()
            plt.plot(temp_array, energy_array,'r')
            plt.xlabel('Temperature (K)')
            plt.ylabel('Helmholtz energy (eV)')
            plt.savefig('Stability_curve.png')
            
        df['temperature']=temp_array
        df['helm_energy']=energy_array
        df['Cv']=cv_array
        df.to_csv('energy_temp.csv',index=False,sep='\t')
        
    
    def get_phonon_thermal(self):
        self.filelist = self.filelist[0]
        for f in self.filelist:  
            if not os.path.exists(f):
                warnings.warn("Phonon_calculation folder is missing!. Program will stop.")
                sys.exit()
            
            os.chdir(f)
            print("Extracting thermal-phonon information in folder {}".format(f))
            if not os.path.exists('vasprun.xml'):
                print('Vasprun.xml file is missing!. Program will stop')
                sys.exit()
            
            self.run_phonopy_thermal()
            print('Successfully created thermal.yaml file.Extracting information from it')
            self.extract_thermal_yaml()
            os.chdir(self.root_dir)
            
    def post_processing(self):
        structures = pd.read_csv(self.root_dir+'/output/preprocessing/structures.csv',header=None).values
        pressures  = pd.read_csv(self.root_dir+'/output/preprocessing/pressures.csv',header=None).values
        df_list = []
        df_final = pd.DataFrame()
        
        for struct in structures:
            df_list_p=[]
            df_final_p = pd.DataFrame()
            for p in pressures:
                df = pd.read_csv(self.root_dir+'/Calcs/Structure-{}/P-{}/Phonon_calculation/energy_temp.csv'.format(struct[0],p[0]),sep='\t')
                energy = df['helm_energy']
                temp   = df['temperature']
                pressure_list = [int(p[0]) for i in range(len(df))]
                df_sp = pd.DataFrame()
                df_sp['energy-Structure-{}'.format(struct[0])] = energy
                df_sp['temp'] = temp
                df_sp['pressure'] = pressure_list
                df_list_p.append(df_sp)
            df_final_p = pd.concat(df_list_p, ignore_index = True)
            df_final_p.to_csv(self.root_dir+'/Calcs/Structure-{}/energy_temp_pressure.csv'.format(struct[0]),index=False)
            
            df_s = pd.read_csv(self.root_dir+'/Calcs/Structure-{}/energy_temp_pressure.csv'.format(struct[0],p[0]))
            df_list.append(df_s)
            
        for df in df_list:
            
            if len(df_final)==0: 
                df_final = df
                
            else:
                df_final = df_final.merge(df, on=['temp','pressure'])
      
        cols = df_final.columns.tolist()
        cols = cols[1:3]+cols[0:1]+cols[3:]
        df_final = df_final[cols]
        if not os.path.exists(self.root_dir+'/output/postprocessing'):
            os.mkdir(self.root_dir+'/output/postprocessing')
        df_final.to_csv(self.root_dir+'/output/postprocessing/energy_temp_pressure_allphases.csv',index=False)
        
        
        for p in pressures:
            df_pressure = df_final[df_final['pressure']==int(p[0])]
            temp = df_pressure['temp']
            df_structs = df_pressure.iloc[:,2:]
            e_min = df_structs.min(axis=1).values
            df_pressure['e_min'] = e_min
            min_struct=df_structs.idxmin(axis="columns").values
            stable_struct=[]
            for st in min_struct:
                stable_struct.append(st.split('energy-')[1])
            df_pressure['stable_struct'] = stable_struct
            df_pressure.to_csv(self.root_dir+'/output/postprocessing/energy_temp_P={}_allphases.csv'.format(int(p[0])),index=False)
            if not os.path.exists(self.root_dir+'/output/results'):
                os.mkdir(self.root_dir+'/output/results')
            if self.make_plots:
                plt.figure()
                for struct in structures:
                    energy = df_pressure['energy-Structure-{}'.format(struct[0])].values
                    plt.plot(temp, energy,label='{}'.format(struct[0]),linewidth=3)
                plt.xlabel('Temperature (K)')
                plt.ylabel('Helmholtz energy (eV)')
                plt.title('Relative-stability-curves-P={} GPa'.format(int(p[0])))
                plt.legend()
                plt.savefig(self.root_dir+'/output/results/Relative-stability-curves-P={}'.format(int(p[0])))
            
