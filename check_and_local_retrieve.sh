#!/bin/bash

singularity exec  `shub-cache shub://khanlab/cfmm2tar:v0.0.1i` ~/autobids/retrieve_cfmm/check_and_local_retrieve.py $@
