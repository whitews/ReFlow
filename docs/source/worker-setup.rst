Worker Setup
============

Guide for setting up a ReFlow Worker client.

#.  Start with a fresh install of 12.04 LTS Server (64-bit).

#.  Install the NVIDIA driver dependencies make, binutils, and gcc:

    ``apt-get install make binutils gcc``

#.  Download the latest nvidia driver:

    ``curl -O http://us.download.nvidia.com/XFree86/Linux-x86_64/331.49/NVIDIA-Linux-x86_64-331.49.run``

#.  Make the installer executable:

    ``chmod +x NVIDIA-Linux-x86_64-331.49.run``

#.  Run the installer and follow the instructions.

    ``./NVIDIA-Linux-x86_64-331.49.run``

#.  Check the driver is working using:

    ``nvidia-smi``

#.  Reboot the server to make sure everything is OK.

#.  Download CUDA 5.5:

    ``curl -O http://developer.download.nvidia.com/compute/cuda/5_5/rel/installers/cuda_5.5.22_linux_64.run``

#.  Make the installer executable:

    ``chmod +x cuda_5.5.22_linux_64.run``

#.  Run the installer, and follow the instructions. Do not install the
    NVIDIA driver when prompted (we have already done this in the previous
    step). However, do choose to install the samples, noting their location.

    ``./cuda_5.5.22_linux_64.run``

#.  Install g++ to test the CUDA installation.

    ``apt-get install g++``

#.  Change directories to the location of the CUDA samples.

#.  Change directories to:

    ``../NVIDIA_CUDA-5.5_Samples/1_Utilities/deviceQuery/``

#.  Run make to build the sample deviceQuery utility.

#.  Once the deviceQuery program compiles, run it and make sure it passes:

    ``./deviceQuery``

#.  Install python-pip and python-dev so we can pip install other Python dependencies:

    ``apt-get install python-pip python-dev``

#.  Install numpy 1.7 using pip:

    ``pip install numpy==1.7.1``

#.  Install scipy dependencies:

    ``apt-get install libblas-dev liblapack-dev gfortran``

#.  Install scipy 0.12 using pip:

    ``pip install scipy==0.12``

#.  Install dpmix dependencies:

    ``pip install cython cyarma cyrand``

    ``apt-get install libarmadillo-dev libboost1.48-dev python-mpi4py``

#.  Install git to clone the flow packages.

    ``apt-get install git``

#.  Clone the gpustats, dpmix, FlowIO, FlowUtils, FlowStats, and ReFlowRESTClient repos:

    ::

        git clone --recursive http://git.tiker.net/trees/pycuda.git
        git clone https://github.com/dukestats/gpustats.git
        git clone https://github.com/andrewcron/dpmix.git
        git clone https://github.com/whitews/FlowIO.git
        git clone https://github.com/whitews/FlowUtils.git
        git clone https://github.com/whitews/FlowStats.git
        git clone https://github.com/whitews/ReFlowRESTClient.git

#.  Make sure you have sudo privileges to install Python packages and install
    all the above. Change to each of the directories and install using setup.py:

    ``python setup.py install``

#.  Create a new worker on the ReFlow server and get the new worker's token from the Django admin site.

#.  On the worker's client machine (Ubuntu) add the worker config file as:

    ``/etc/reflow_worker.conf``

#.  Edit the file and add the JSON content (edit with proper values):

    ::

        {
            "host": "<reflow_server_ip_address",
            "name": "<worker_name>",
            "token": "<worker_token>"
        }


#.  As root, from the ``ReFlowWorker/reflowworker`` directory, start the worker:

    ``python worker.py start``