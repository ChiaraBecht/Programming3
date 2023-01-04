# Assignment 6
The scripts in this folder can be used to produce mappings for a minion sequencing run and extracting annotations (GO function annotations and EC numbers) for the resulting mapping file (sam formatted) in a distributed and parallel fashion. The task is split into two components: generating the mappings. This taks is conducted using the mapping tool minimap2 command line based. The mapping file is then processed by a python script in distributed and parallel fashion. The subtasks are extracting gi_id, start and stop postition per read from the mapping file, downloading the reference genbank file from ncbi, extracting annotations from the genbank file for given read range.
The mapping step is conducted in parallel, exploiting the tools multiprocessing option. The mapping task is scheduled using SLURM. The annotation step is conducted distributed and parallel using python library multiprocessings server client model and queue objects. I have worked with 4 clients and 3 peons per client. More clients and peons can be used based on available resources. Every job corresponds to a single line of the mapping file. Bigger data packages can be created by using the sectioning function in the test folders and adding loops to execute the instructions for every line in the data package given.
## Program structure
- assignment6.sh: produce mappings
- Server_Client_new.py: produce results
- Helper functions: config file parser, functions to read and process mapping file, query ncbi and download genbank files, extract annotations, result presentation scripts
## Instructions
Produce a single mapping file or several by running the assignment6.sh script. I have pre-selected standard parameter settings and one variation. If you want to add another mapping run add it to assignment6.sh, don't forget to adjust the runtime estimate in the SLURM job set up. Furthermore, dont forget to add run number to the file name. Run the assignment6.sh from command line using:
- > sbatch assignment6

For each mapping file (in my case run_1 and run_2) a server and its corresponding servers need to be started to get the annotation statistics. The server and clients need to be started from command line while connected to the network and inside a tmux session. Setup for run 1:
- Server
> python3 path/to/Server_Client_new.py -r run_1 -n 1 -s --port portnum --host host_name
- Client_1
> python3 path/to/Server_Client_new.py -r run_1 -n num_peons -c --port portnum --host host_name
- Client_2
> python3 path/to/Server_Client_new.py -r run_1 -n num_peons -c --port portnum --host host_name
- ...
- Client_n
> python3 path/to/Server_Client_new.py -r run_1 -n num_peons -c --port portnum --host host_name

Importantly, the portnumber can be anything in the range of available portnumbers. The host name is the name of the host the server is run on. For the clients to connect the portnumber and the hostname is the same one the server has, even though they are initiated from another node of the cluster. The number of process/peons per client depends on physical cores available. As a rule of thumb double number of physical cores is the max that can be used to remain efficient. Dependend on how much of the cluster you are allowed to use for your task, you can launch a second server and its clients to process the run 2. Note, some of the parameters (mapping file location + mapping file name, path to output folder, path to genbank file cache) are defined in a config file. You have to edit the config file accordingly for your needs and run conditions.
