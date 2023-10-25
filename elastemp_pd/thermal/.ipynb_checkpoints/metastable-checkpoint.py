import pandas as pd, os, sys, warnings
import os.path as osp
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB 
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn import datasets
import numpy as np
import matplotlib.pyplot as plt
from mlxtend.plotting import plot_decision_regions
import matplotlib.gridspec as gridspec
import itertools



class get_metastable:
    def __init__(self,g_min,g_max,num_g):
        self.g_min = g_min
        self.g_max = g_max
        self.num_g = num_g
        self.root_dir = os.getcwd()
        self.check_input_files()
        self.compute_metastable_energies()
        self.extrapolate()
        self.compute_metastable_energies_extrapolate()
        
        
    
    
    def check_input_files(self):
       
        if not os.path.exists(self.root_dir+'/output/postprocessing/energy_temp_pressure_allphases.csv'):
            warnings.warn('Unable to read energy_temp_pressure_allphases.csv. Please check output/postprocessing if file is missing!')
        if self.g_min>self.g_max:
            warnings.warn("g_min and g_max need to be greater than equal to zero. g_max needs to be greater than g_min")
            sys.exit()
        if self.num_g <=0:
            warnings.warn("number of g interval points need to be greater than 0")
            sys.exit()          
            
            
    def extrapolate(self):
        df = pd.read_csv(self.root_dir+'/output/postprocessing/energy_temp_pressure_allphases.csv')
        structures = pd.read_csv(self.root_dir+'/output/preprocessing/structures.csv',header=None).values
        pressures  = pd.read_csv(self.root_dir+'/output/preprocessing/pressures.csv',header=None).values
        p_min = min(pressures)[0]
        p_max = max(pressures)[0]
        if len(pressures)<4:
            warnings.warn('Less than 4 pressure points found. Cannot extrapolate')
            sys.exit()
        else:
            poly_degree = 4
        
        df_final = pd.DataFrame()
        for s in structures:       
            df_temp = df[['temp','pressure','energy-Structure-{}'.format(s[0])]]
            num_temp = df_temp['temp'].unique()
            df_struct = pd.DataFrame()
            for t_step in num_temp:
                df_temp_temp = df_temp[df_temp['temp']==t_step]
                x = df_temp_temp['pressure'].values
                y = df_temp_temp['energy-Structure-{}'.format(s[0])].values
                poly_fit = np.polyfit(x,y,poly_degree)
                df_new = pd.DataFrame()
                p_fit=[]; e_fit= [];t_fit = []
                for p_step in range(p_min,p_max+1):
                    p_fit.append(p_step)
                    e_fit.append(poly_fit[0]*p_step**(4)+poly_fit[1]*p_step**3+poly_fit[2]*p_step**2+poly_fit[3]*p_step**1+poly_fit[4]*p_step**0)
                    t_fit.append(t_step)
                df_new['temp'] = t_fit
                df_new['pressure'] = p_fit
                df_new['energy-Structure-{}'.format(s[0])] = e_fit

                if len(df_struct)==0:
                    df_struct = df_new
                else:
                    df_struct = pd.concat([df_struct,df_new],ignore_index=True,axis=0)
            
            if len(df_final)==0:
                df_final = df_struct
            else:
                df_final = pd.merge(df_final, df_struct, how="inner", on=["temp", "pressure"])
        df_final.to_csv(self.root_dir+'/output/postprocessing/energy_temp_pressure_allphases_extrapolated.csv',index=False)
            
    
    
    def compute_metastable_energies(self):
        self.g_list = [round(self.g_min+(self.g_max-self.g_min)*i/self.num_g,2) for i in range(self.num_g+1)]
        df_energy = pd.read_csv(self.root_dir+'/output/postprocessing/energy_temp_pressure_allphases.csv')   
        df_structs = df_energy.iloc[:,2:]
        df_tp = df_energy.iloc[:,0:2]
        e_min = df_structs.min(axis=1).values
        df_structs['e_min'] = e_min  
        for i in range(len(self.g_list)):
            df_structs = df_energy.iloc[:,2:]
            df_tp = df_energy.iloc[:,0:2]
            e_min = df_structs.min(axis=1).values
            df_structs['e_min'] = e_min
            dg_val = self.g_list[i]
            dg = [dg_val for i in range(len(df_structs))]
            df_structs['dg'] = dg
        
            for col in df_structs.columns:
                if col=='e_min' or col=='dg':
                    pass
                else:
                    df_structs[col]=df_structs[col]-df_structs['e_min']-df_structs['dg']
       
            df_structs[df_structs<0]=10
            min_struct=df_structs.iloc[:,:-2].idxmin(axis="columns").values
            stable_struct=[]
            
            for st in min_struct:
                stable_struct.append(st.split('energy-Structure-')[1])
            df_structs = df_structs.iloc[:,:-2]
            df_structs['stable_struct_class'] = stable_struct
            df_energy_g = df_tp.join(df_structs)
            df_energy_g.to_csv(self.root_dir+'/output/postprocessing/relative_energies_dg={}.csv'.format(dg_val),index=False)
            df_tp['stable_struct'] = stable_struct
            df_tp.to_csv(self.root_dir+'/output/postprocessing/stable_phase_dg={}.csv'.format(dg_val),index=False)
                        
        
        
    def compute_metastable_energies_extrapolate(self):
        print('Extrapolating each structure energies at each temperature across different pressures')
        self.g_list = [round(self.g_min+(self.g_max-self.g_min)*i/self.num_g,2) for i in range(self.num_g+1)]
        df_energy = pd.read_csv(self.root_dir+'/output/postprocessing/energy_temp_pressure_allphases_extrapolated.csv')   
        df_structs = df_energy.iloc[:,2:]
        df_tp = df_energy.iloc[:,0:2]
        e_min = df_structs.min(axis=1).values
        df_structs['e_min'] = e_min  
        for i in range(len(self.g_list)):
            df_structs = df_energy.iloc[:,2:]
            df_tp = df_energy.iloc[:,0:2]
            e_min = df_structs.min(axis=1).values
            df_structs['e_min'] = e_min
            dg_val = self.g_list[i]
            dg = [dg_val for i in range(len(df_structs))]
            df_structs['dg'] = dg
        
            for col in df_structs.columns:
                if col=='e_min' or col=='dg':
                    pass
                else:
                    df_structs[col]=df_structs[col]-df_structs['e_min']-df_structs['dg']
       
            df_structs[df_structs<0]=10
            min_struct=df_structs.iloc[:,:-2].idxmin(axis="columns").values
            stable_struct=[]
            for st in min_struct:
                stable_struct.append(st.split('energy-Structure-')[1])
            df_structs = df_structs.iloc[:,:-2]
            df_structs['stable_struct_class'] = stable_struct
            df_energy_g = df_tp.join(df_structs)
            df_energy_g.to_csv(self.root_dir+'/output/postprocessing/relative_energies_dg={}_extrapolated.csv'.format(dg_val),index=False)
            df_tp['stable_struct'] = stable_struct
            df_tp.to_csv(self.root_dir+'/output/postprocessing/stable_phase_dg={}_extrapolated.csv'.format(dg_val),index=False)
            self.get_slices(dg_val)
        
        
        
    def get_slices(self,dg):
        
        df = pd.read_csv(self.root_dir+"/output/postprocessing/stable_phase_dg={}_extrapolated.csv".format(dg))
        dg_val = int(dg*1000)
        print("Extracting metastable slices at dg = {} eV/atom from ground state".format(dg))
        print("Slices will be output/results dir")
        
        clf1 = LogisticRegression(random_state=1, solver='newton-cg', multi_class='multinomial')
        clf2 = RandomForestClassifier(random_state=1, n_estimators=100)
        clf3 = GaussianNB()
        clf4 = SVC(gamma='auto')
        X = df.iloc[:,0:2].values
        y = df.iloc[:,-1].values
        gs = gridspec.GridSpec(2, 2)
        
        labels = ['Logistic Regression', 'Random Forest', 'Naive Bayes', 'SVM']
        for clf, lab, grd in zip([clf1, clf2, clf3, clf4], labels, itertools.product([0, 1], repeat=2)):
            clf.fit(X, y)
            fig = plt.figure(figsize=(10,8))
            fig = plot_decision_regions(X=X, y=y, clf=clf, legend=2)
            plt.xlabel('Temperature (K)')
            plt.ylabel('Pressure (GPa)')
            plt.title(lab)
            plt.legend(bbox_to_anchor=(1.05, 1))
            fig_path = osp.join(self.root_dir,"output/results")
            plt.savefig(fig_path+"/Metastable_slice_{}_dG={}.png".format(lab,dg_val))
            
        