Worker Setup
============

Guide for setting up a ReFlow Worker client.

#.  Start with a fresh install of 14.04 LTS Server (64-bit). Update and upgrade system packages:

    ::

        apt-get update
        apt-get upgrade

#.  Install latest kernel:

    ::

        apt-get install linux-image-virtual

    .. note:: On virtual machines (such as the GPU instances on Amazon EC2), you will also need to install the package ``linux-image-extra-virtual``.

#.  Reboot the system to ensure the kernel update was successful.

#.  Add the "restricted" option to the trusty-updates deb repository. In the file ``/etc/apt/sources.list``, find and change this line:

    ::

        deb http://us.archive.ubuntu.com/ubuntu/ trusty-updates main

    to:

    ::

        deb http://us.archive.ubuntu.com/ubuntu/ trusty-updates main restricted

    .. note:: The URL of the apt repository may be different on your system.

#.  Update the apt packages:

    ::

        apt-get update

#.  Install the NVIDIA driver via apt-get, choosing the current "tested" version (currently 346.96):

    ::

        apt-get install nvidia-346 nvidia-prime

#.  Reboot the server and check the driver is working using:

    ::

        nvidia-smi

#.  Download the CUDA 7.0 installer:

    ::

        curl -O http://developer.download.nvidia.com/compute/cuda/7_0/Prod/local_installers/cuda_7.0.28_linux.run

#.  Make the installer executable, but do not install cuda yet:

    ::

        chmod +x cuda_7.0.28_linux.run

#.  Extract the various cuda installers to a new directory:

    ::

        mkdir cuda-installer
        mv cuda_7.0.28_linux.run cuda-installer
        cd cuda-installer
        ./cuda_7.0.28_linux.run -extract=`pwd`

#.  Run the isolated cuda installer, and follow the instructions:

    ::

        ./cuda-linux64-rel-7.0.28-19326674.run

#.  Install the cuda samples, noting their install location:

    ::

        ./cuda-samples-linux-7.0.28-19326674.run

#.  Edit any user profiles (~/.profile) to add the paths to the cuda compiler and libraries:

    ::

        PATH=/usr/local/cuda/bin:$PATH
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib:/usr/local/cuda/lib64

#.  Either logout or source the profile to update the paths.

#.  Install tools to build the CUDA samples to test the CUDA installation:

    ::

        apt-get install build-essential

#.  Change directories to the location of the CUDA samples.

    ::

        cd /usr/local/cuda/samples

#.  Change directories to the device query example:

    ::

        cd 1_Utilities/deviceQuery/

#.  Run make to build the sample deviceQuery utility.

    ::

        make

#.  Once the deviceQuery program compiles, run it and make sure it passes:

    ::

        ./deviceQuery

#.  Install dependencies for PyCUDA:

    ::

        apt-get install python-dev python-setuptools
        apt-get install python-numpy
        apt-get install libboost-dev

#.  Install git:

    ::

        apt-get install git

#.  Clone the PyCUDA git repository from Github:

    ::

        git clone --recursive http://git.tiker.net/trees/pycuda.git

#.  Install PyCUDA:

    ::

        cd pycuda/
        ./configure.py
        make
        python setup.py install

#.  Install ipython (optional) and test the PyCUDA installation:

    ::

        apt-get install ipython
        ipython
        import pycuda._driver as drv
        drv.init()
        quit

#.  Install gpustats:

    ::

        git clone https://github.com/whitews/gpustats.git
        cd gpustats/
        python setup.py install

#.  Install cyarma and cyrand:

    ::

        git clone https://github.com/andrewcron/cyrand.git
        git clone https://github.com/andrewcron/cy_armadillo.git
        cd cyrand/
        python setup.py install
        cd ../cy_armadillo/
        python setup.py install

#.  Install dpmix dependencies:

    ::

        apt-get install python-scipy cython libarmadillo-dev python-mpi4py

#.  Install dpmix from the development branch:

    ::

        git clone https://github.com/andrewcron/dpmix.git
        cd dpmix
        git checkout develop
        python setup.py install

#.  Clone the git repositories for the various flow libraries:

    ::

        git clone https://github.com/whitews/FlowIO.git
        git clone https://github.com/whitews/FlowUtils.git
        git clone https://github.com/whitews/FlowStats.git

#.  Install the flow libraries:

    ::

        cd FlowIO
        python setup.py install
        cd ../FlowUtils
        python setup.py install
        cd ../FlowStats
        python setup.py install

#.  Install the Python library requests (dependency for the ReFlow REST client):

    ::

        apt-get install python-requests

#.  Clone and install the ReFlow REST client:

    ::

        git clone https://github.com/whitews/ReFlowRESTClient.git
        cd ReFlowRESTClient
        python setup.py install

#.  Clone the ReFlowWorker repository (but do not install):

    ::

        git clone https://github.com/whitews/ReFlowWorker.git

#.  Create a new worker on the ReFlow server and get the new worker's token.

#.  On the worker's client machine (Ubuntu) add the worker config file ``/etc/reflow_worker.conf``.

#.  Edit the file and add the JSON content (edit with proper values):

    ::

        {
            "host": "<reflow_server_ip_address",
            "name": "<worker_name>",
            "token": "<worker_token>",
            "devices": <list of GPU device numbers>
        }

#.  As root, from the ``ReFlowWorker/reflowworker`` directory, start the worker:

    ::

        python worker.py start