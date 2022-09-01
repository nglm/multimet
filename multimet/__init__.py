# We typically want:
#
# import multimet as mm
# from multimet.preprocess import mjo
# members, time = mm.preprocess.mjo()

# We do that to skip the persistent graph folder (which itself
# skip the persistentgraph.py file and access the class directly)
from . import preprocess

