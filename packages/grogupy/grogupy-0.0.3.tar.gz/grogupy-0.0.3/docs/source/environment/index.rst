Environment Variables
=====================

Environment variables are key-value pairs that can
affect the way running processes will behave on a computer.

Setting Environment Variables
------------------------------

1. **LD_LIBRARY_PATH**: This variable specifies the directories
   where the system should look for dynamic libraries. For example,
   to ensure that CuPy can find the necessary CUDA libraries, you
   might need to set the `LD_LIBRARY_PATH` as follows:

.. code-block:: bash

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/software/packages/cuda/12.3/targets/x86_64-linux/lib

2. **grogupy_ARCHITECTURE**: This variable sets the architecture
   for the grogupy project. By default, the architecture is set to
   CPU. To change it to GPU, you can set the `grogupy_ARCHITECTURE`
   environment variable:

.. code-block:: bash

    export grogupy_ARCHITECTURE=GPU
