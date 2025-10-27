from Qt import QtWidgets
from NodeGraphQt import BaseNodeCircle

class GDRomNode(BaseNodeCircle):
    __identifier__ = 'gdrom' # unique node identifier domain.
    NODE_NAME = 'GD-ROM'     # initial default node name.

    def __init__(self):
        super(GDRomNode, self).__init__()
        # Outputs
        self.add_output('LEFT')
        self.add_output('RIGHT')

#TODO: GDROM: everything (play/stop/pause, and level/pan controls ?)