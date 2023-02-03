# Templates
A number of template files; GYRE inlists, bash scripts, VSC submit files.

## Contents
1. `run_MESA.sh`: bash script to run MESA and make error and log files.
2. `SLURM_submit_list_template`: Template to submit a jobarray to SLURM.
3. `VSC_SLURM_submit_MESA.pbs`: pbs file to submit a jobarray on the VSC to the SLURM scheduler, running `run_MESA.sh` with a range of parameters.
4. `VSC_submit_MESA.pbs`: pbs file to submit a jobarray on the VSC, running `run_MESA.sh` with a range of parameters. (VSC will move away from this system in april 2023)
