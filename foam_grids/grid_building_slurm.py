"""Functions for building MESA and GYRE grids on the SLURM framework."""
# from foam import grid_building_slurm as gbs
import numpy as np
import os, sys
from pathlib import Path
from shutil import copyfile
import logging
from grids_tutorial import support_functions as sf

logger = logging.getLogger('logger.gbs')
################################################################################
def write_bash_submit( jobname, list, bash_submit_list, walltime=1440, memory=3000, cpu=1,
                       bash_template = os.path.expandvars(f'{Path(__file__).parent}/templates/SLURM_submit_list_template.sh')
                      ):
    """
    Write a bash script to sumbit a list of jobs to SLURM.
    ------- Parameters -------
    jobname, list, bash_submit_list: string
        name of the job, path to the list to submit, name of the file for the bash script
    bash_template: string
        path to the template of the bash script to read and modify
    walltime, memory, cpu: int
        specifying walltime (minutes), memory (mb) and number of cpus per task
    """
    with open(bash_template, 'r') as f:
            lines = f.readlines()
    replacements = {'JOBNAME' : f'{jobname}',
                    'WALLTIME': f'{walltime}',
                    'MEMORY'  : f'{memory}',
                    'CPU'     : f'{cpu}',
                    'LIST'    : f'{list}' }

    new_lines = []
    for line in lines:
        new_line = line
        for key in replacements:
                if (replacements[key] != ''):
                        new_line = new_line.replace(key, replacements[key])
        new_lines.append(new_line)
    logger.info(f'write {bash_submit_list}')

    with open(bash_submit_list, 'w') as f:
        f.writelines(new_lines)
    return

################################################################################
def make_mesa_setup(setup_directory=f'{os.getcwd()}/MESA_setup', output_dir=f'{os.getcwd()}/MESA_out',
                    work_dir=f'{os.getcwd()}/MESA_work_dir', Z_ini_list=[0.014], M_ini_list=[1], log_Dmix_list=[1], aov_list=[0], fov_list=[0]):
    """
    Construct a setup for a MESA grid with job lists to run on e.g. SLURM, and bash scripts to run each job list.
    ------- Parameters -------
    setup_directory, output_dir, work_dir: string
        paths to the directory where the bash setup is being made, to the directory where the MESA output will be stored, and to the MESA work directory.
    Z_ini_list, M_ini_list, log_Dmix_list, fov_list, aov_list: list of floats
        Lists of the parameter values to be computed in the grid.
    """
    if not os.path.exists(work_dir):
        logger.error(f'Specified MESA work directory does not exist: {work_dir}')
        sys.exit()
    Path(f'{setup_directory}/submit-lists-scripts').mkdir(parents=True, exist_ok=True)
    Path(f'{setup_directory}/lists').mkdir(parents=True, exist_ok=True)

    params_to_run = []
    lines_run_all_bash = []
    lines_run_all_bash.append('#!/bin/bash \n')

    index = 0
    parameter_combinations = len(Z_ini_list)*len(M_ini_list)*len(log_Dmix_list)*len(aov_list)*len(fov_list)

    for Z_ini in Z_ini_list:
        Z_ini = f'{Z_ini:.3f}'
        for M_ini in M_ini_list:
            M_ini = f'{M_ini:.2f}'
            for log_Dmix in log_Dmix_list:
                log_Dmix = f'{log_Dmix:.2f}'
                for a_ov in aov_list:
                    a_ov = f'{a_ov:.3f}'
                    for f_ov in fov_list:
                        f_ov = f'{f_ov:.3f}'

                        params_to_run.append(f'{setup_directory}/run_MESA.sh {Z_ini} {M_ini} {log_Dmix} {a_ov} {f_ov} {output_dir} {work_dir} \n')
                        index += 1
                        if index%1000 == 0 or index == parameter_combinations:
                            list_nr = int(np.floor(index/1000))+1
                            list_to_run_path = f'{setup_directory}/lists/list{list_nr}'
                            write_bash_submit(f'MESA{list_nr}', list_to_run_path, f'{setup_directory}/submit-lists-scripts/submit_list{list_nr}.sh')
                            # logger.info(f'write {list_to_run_path}')
                            with open(list_to_run_path, 'w') as f:
                                f.writelines(params_to_run)
                            params_to_run = []

                            if index%1000 == 0:
                                lines_run_all_bash.append(f'sbatch --array=1-1000 {setup_directory}/submit-lists-scripts/submit_list{list_nr}.sh \n')
                            else:
                                lines_run_all_bash.append(f'sbatch --array=1-{parameter_combinations%1000} {setup_directory}/submit-lists-scripts/submit_list{list_nr}.sh \n')


    lines_run_all_bash = sorted(lines_run_all_bash)     #A bash script to submit all other bash scripts
    with open(f'{setup_directory}/submit_all_bash.sh', 'w') as fobj:
        fobj.writelines(lines_run_all_bash)

    copyfile(os.path.expandvars(f'{Path(__file__).parent}/templates/run_MESA.sh'), f'{setup_directory}/run_MESA.sh')
    return
