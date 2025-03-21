import faulthandler
faulthandler.enable()
import gzip
import requests
from io import BytesIO
from tiny_tf.tf import Transform
from yag_slam.models import LocalizedRangeScan
from yag_slam.graph_slam import GraphSlam
from yag_slam.helpers import default_config, default_config_loop
from yag_slam.scan_matching import Scan2DMatcherCpp
default_config["resolution"] = 0.001
Scan2DMatcherCpp(default_config)