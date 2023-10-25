# elastemp-pd

Elastemp-pd is a workflow integrating VASP, Phonopy and Machine learning to estimate the metastable phase diagrams (P-T) of materials. (ie phase diagrams at different extents of metastability from ground state). This workflow can be used either via command line by altering the main file or can be used in a Jupyter notebook (example given). 

# Setting the environment

Python packages needed to run this code are numpy, matplotlib, pandas, pymatgen and phonopy. Users can either pip these or use the more convenient environment.yml file as

conda env create -f environment.yml

conda activate Elastemp-env

# Files needed

To run vasp calculations, user needs to input the structure file of the structures and the potential file.

The structure file needs to be input in the form of POSCAR-1, POSCAR-2 format in a directory. It is recommended to save this directory as 'POSCARS'. Else, change the directory name in the main file make_zero_enthalpy command. 

# Workflow

The workflow of elastemp-pd consists of 5 parts with a python command for each. 

## Make zero enthalpy:

This section creates the folders 'Calcs' and 'Structure-*/P-*' for each structure with the required input files for vasp calculations and 'output' folder to save the output data. 

Python command : make_zero_enthalpy(root_dir = 'POSCARS', kptdensity=6000, p_min = 0, p_max = 100, num_p=4)

The user parameters that can be varied are kptdensity (higher kpt density results in tighter k point grid), p_min, p_max and num_p corresponding to the minimum, maximum and number of pressure points equally spaced in between. So p_min = 0, p_max=100 and num_p=4 results in pressure points of 0, 25, 50, 75, 100 GPa. Each folder has an INCAR file which is provided by default in each of the folders. Users can modify it. 

Users need to run vasp in these folders. The directories in which the vasp calculations need to be run is saved in output/preprocessing/filelist_enthalpy.csv file. 

## Get zero enthalpy

This section extracts the enthalpies from the vasp calculations. 

Python command : get_zero_enthalpy()

This extracts the enthalpies and calculates the zero point enthalpy ZPE.txt in each folder. 

## Make phonon

This section generates supercells for structure in the Calcs/Structure-*/P-*/Phonon_calculation folder.  Supercell dimension needs to be input in the form of a three dim list such as [2,2,2]. The k-point density can be changed to generate tighter or looser k-point grids. Since the size of cell is now bigger, a lower k pt grid is generally sufficient. A default INCAR file is provided if not given in the home directory (needs to be called INCAR_dynamic). For most cases, the default INCAR works well.A copy of list of files to be run is stored in the output/preprocessing directory as filelist_dynamic.csv

Python command : make_phonon(dim=[2,2,2], kptdensity=500)

## Get phonon

Calculates the force constants in each structure/pressure/phonon calculation folder. 

Python command: get_phonon()

## Get thermal

This command calculates the quasi-harmonic energies in each structure-p folder. The input parameters are the supercell dimension, minimum temperature and maximum temperature between which quasi-harmonic approximation is done with the interval period of t_step. Usually 10 K is sufficient as t_step. Going further below will cause computational time to increase significantly. If make_plots is set as true, relative stability curves (ie G vs T for all phases) at different pressures are computed and plotted in output/results folder

Python command : get_thermal(dim=[2,2,2], t_min=0, t_max = 1000, t_step=10, make_plots=True)

## Get metastable

This will extract metastable slices at different dG intervals. The input parameters are g_min, g_max ie the range of energy values of metastablitiy. The number of slices in between them is given as num_g. if num_g is 2, slices are calculated at dG = 0, dg = 0.2, dg = 0.4 from ground state. From the raw data of the stable phases at each P-T, 4 classifiers- logistic regression, random forest, Naive bayes and SVM classifiers are fit to plot decision boundaries. For best results, manual intervention needs to be made with domain knowledge. 

python command: get_metastable(g_min=0,g_max=0.04,num_g=2)
