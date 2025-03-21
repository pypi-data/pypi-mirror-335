# -*- coding: utf-8 -*-
import os
import sys

# add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from service_basic_pipservices.containers.BasicProcess import BasicProcess

proc = BasicProcess()
proc._config_path = "./config/config.yml"
proc.run()
