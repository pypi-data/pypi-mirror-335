import warnings
warnings.filterwarnings("ignore")

from .data.local_dataset import LocalDataSet as DataSet
from .models.local_model_zoo import LocalModelZoo as ModelZoo
from .testsuite.local_testsuite import LocalTestSuite as TestSuite

import sys
import logging
logging.disable(sys.maxsize)

__all__ = ["DataSet", "ModelZoo", "TestSuite"]

__version__ = '1.0.9'
__date__ = "2025.03"
__author__ = 'Modeva Dev Team'
