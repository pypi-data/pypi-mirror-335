.. _running_in_hpc:

Running grogupy in HPC
======================

This section provides instructions on how to configure
and run grogupy on a High-Performance Computing (HPC)
system using SLURM. Below is an example of a bash script
for submitting a job to the SLURM scheduler.

Example SLURM Batch Script
---------------------------

The following is an example SLURM batch script (`sbatch`)
for running grogupy on an HPC system, in this case on
`Komondor <https://hpc.kifu.hu/hu/komondor>`_.:

.. code-block:: bash

    #!/bin/bash
    #SBATCH --job-name=grogupy
    #SBATCH --nodes=1
    #SBATCH --ntasks=1
    #SBATCH --ntasks-per-node=1
    #SBATCH --cpus-per-task=128
    #SBATCH --time=01:00:00
    #SBATCH --gres=gpu:8
    #SBATCH --partition=ai
    #SBATCH --exclusive
    #SBATCH --mem-per-cpu 4000

    ulimit -s unlimited

    source ~/.bashrc
    yes | module clear
    module purge
    module load PrgEnv-gnu cray-pals cray-python cuda/12.3

    export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
    export OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK
    export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK
    export VECLIB_MAXIMUM_THREADS=$SLURM_CPUS_PER_TASK
    export NUMEXPR_NUM_THREADS=$SLURM_CPUS_PER_TASK

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/software/packages/cuda/12.3/targets/x86_64-linux/lib
    export grogupy_ARCHITECTURE=GPU

    time srun grogupy ./grogupy_input.py

Explanation of the Script
-------------------------

- `#SBATCH --job-name=grogupy`: Sets the name of the job.
- `#SBATCH --nodes=1`: Requests one node.
- `#SBATCH --ntasks=1`: Requests one task.
- `#SBATCH --ntasks-per-node=1`: Specifies one task per node.
- `#SBATCH --cpus-per-task=128`: Allocates 128 CPUs per task.
- `#SBATCH --time=06:00:00`: Sets a time limit of 1 hours for the job.
- `#SBATCH --gres=gpu:8`: Requests 8 GPUs.
- `#SBATCH --partition=ai`: Specifies the partition to submit the job to.
- `#SBATCH --exclusive`: Ensures exclusive access to the node.
- `#SBATCH --mem-per-cpu 4000`: Allocates 4000 MB of memory per CPU.

The script also sets up the environment by loading necessary
modules and setting environment variables for optimal
performance. Exportin the LD_LIBRARY_PATH variable is necessary
to ensure that the CUDA library is accessible for cupy. The
script also sets the `grogupy_ARCHITECTURE` environment
variable to `GPU` to enable GPU acceleration in grogupy.
Finally, it runs the grogupy application using `srun` and the
`grogupy` command line script.

Make sure to adjust the script parameters according to
your HPC system's configuration and your specific requirements.


Example input file format
-------------------------

This is the corresponding input file for the above script, `grogupy_input.py`,
which contains the parameters for the grogupy simulation. These variables
are passed to the appropriate functions in the grogupy package very similarly
as we did in the jupyter notebook examples.

.. code-block:: python

    # input folder and file
    infolder = "./"
    infile = "CrIWSe.fdf"
    # kset should be at leas 100x100 for 2D diatomic systems
    kset = [10, 10, 1]
    # eset should be 100 for insulators and 1000 for metals
    eset = 100
    # esetp should be 600 for insulators and 10000 for metals
    esetp = 600
    # emin None sets the minimum energy to the minimum energy in the eigfile
    emin = None
    # emax is at the Fermi level at 0
    emax = 0
    # the bottom of the energy contour should be shifted by -5 eV
    emin_shift = -5
    # the top of the energy contour can be shifted to the middle of the gap for insulators
    emax_shift = -0.22
    # usually the DFT calculation axis is [0, 0, 1]
    scf_xcf_orientation = [0, 0, 1]
    # the reference directions for the energy derivations
    ref_xcf_orientations = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    # matlabmode is only for testing purposes
    matlabmode = False

    # magnetic entities and pairs can be defined automatically from the cutoff radius and magnetic atoms
    setup_from_range = True
    radius = 4
    atomic_subset = "Cr"

    # sequential solver is better for large systems
    greens_function_solver = "Sequential"
    # always use K for now
    parallel_mode = "K"
    # the calculation of J and K from the energy derivations, either Fit or grogupy
    exchange_solver = "Fit"
    anisotropy_solver = "Fit"

    # save the magnopy file
    save_magnopy = True
    # precision of numerical values in the magnopy file
    magnopy_precision = None
    # add the simulation parameters to the magnopy file as comments
    magnopy_comments = True

    # save the pickle file
    save_pickle = True
    # add all the arrays to the pickle file, which can be large
    pickle_dump_all = False

    # output folder, for example the current folder
    outfolder = infolder
    # outfile name
    outfile = f"CrIWSe_kset_{'_'.join(map(str, kset))}_eset_{eset}"
