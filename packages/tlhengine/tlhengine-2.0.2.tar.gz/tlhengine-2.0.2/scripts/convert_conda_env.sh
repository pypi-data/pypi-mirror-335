# this file is used to handle the shit of conda list -e > requirements.txt
# because the result text contains both conda and pip packages
# so simply conda env create -n <env_name> -f requirements.txt will raise error that pip packages can't find

# this script can split the file into separete files

# in fact, a better way to share env is by using
# conda env export > env.yml
# in this case, simply using
# conda env create -f env.yml will automatically call pip

# but this script is in case of some bad developer use the bad operation.
grep -v '=py' requirements.txt > conda_req.txt
grep '=py' requirements.txt | sed 's/=py.*//' | sed 's/=/==/'  > pip_req.txt