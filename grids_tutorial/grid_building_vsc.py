"""Functions for building MESA and GYRE grids on the VSC (Vlaams Supercomputer Centrum) framework."""
# from foam import grid_building_vsc as gbv
import os, sys, csv
import logging
from shutil import copyfile
from pathlib import Path
from grids_tutorial import support_functions as sf

logger = logging.getLogger('logger.gbv')
################################################################################
def make_mesa_setup(setup_directory=f'{os.getcwd()}/MESA_setup', work_dir=f'{os.getcwd()}/MESA_work_dir',
                    Z_ini_list=[0.014], M_ini_list=[1], log_Dmix_list=[1], aov_list=[0], fov_list=[0],
                    output_dir= os.path.expandvars(f'{os.getcwd()}/MESA_out')):
    """
    Construct a setup and job list to run a MESA grid on the VSC.
    Check the submission script 'submit_MESA.pbs' that is copied by this function
    for instructions on how to run the grid on the VSC using the worker frame.
    ------- Parameters -------
    setup_directory, output_dir, work_dir: string
        paths to the directory with the MESA job submission files, the MESA output folder, and to the MESA work directory.
    Z_ini_list, M_ini_list, log_Dmix_list, fov_list, aov_list: list of floats
        Lists of the parameter values to be computed in the grid.
    """
    for directory_name in [setup_directory, work_dir, output_dir]:
        if 'site_scratch' in directory_name:
            directory_name = directory_name[directory_name.rfind("site_scratch"):].replace('site_scratch', '/scratch')

    if not os.path.exists(work_dir):
        logger.error(f'Specified MESA work directory does not exist: {work_dir}')
        sys.exit()
    Path(f'{setup_directory}').mkdir(parents=True, exist_ok=True)

    with open(f'{setup_directory}/MESA_parameters.csv', 'w') as tsvfile:
        writer = csv.writer(tsvfile)
        header = ['Zini', 'Mini', 'logD', 'aov', 'fov', 'output_dir', 'MESA_work_dir']
        writer.writerow(header)

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

                            line_to_write = [Z_ini, M_ini, log_Dmix, a_ov, f_ov, output_dir, work_dir]
                            writer.writerow(line_to_write)

    copyfile(os.path.expandvars(f'{Path(__file__).parent}/templates/run_MESA.sh'), f'{setup_directory}/run_MESA.sh')
    copyfile(os.path.expandvars(f'{Path(__file__).parent}/templates/VSC_submit_MESA.pbs'), f'{setup_directory}/submit_MESA.pbs')
    return
