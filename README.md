# elastemp-pd

Elastemp-pd is a workflow integrating VASP, Phonopy and Machine learning to estimate the metastable phase diagrams of materials. (ie phase diagrams at different extents of metastability from ground state). This workflow can be used either via command line by altering the main file or can be used in a Jupyter notebook (example given). 

# Setting the environment

Python packages needed to run this code are numpy, matplotlib, pandas, pymatgen and phonopy. Users can either pip these or use the more convenient environment.yml file as

conda env create -f environment.yml

conda activate Elastemp-env

# Files needed

To run vasp calculations, user needs to input the structure file of the structures and the potential file.

The structure file needs to be input in the form of POSCAR-1, POSCAR-2 format in a directory. It is recommended to save this directory as 'POSCARS'. Else, change the directory name in the main file make_zero_enthalpy command. 

