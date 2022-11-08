# We typically want:
#
# import multimet as mm
# from multimet.preprocess import mjo
#
# members, time = mm.preprocess.mjo()
#
# mm.utils.save_as_json(obj, filename)

from . import preprocess
from . import stats
from . import utils
