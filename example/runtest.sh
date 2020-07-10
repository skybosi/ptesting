#!/bin/bash

# unit
## normal
python ../src/request.py ./unit
## ctrl stdout
python ../src/request.py ./unit -1

# count
## normal
python ../src/request.py ./count
## ctrl stdout
python ../src/request.py ./count -1

# flow
## normal
python ../src/request.py ./flow
## ctrl stdout
python ../src/request.py ./flow -1
