class MsgCancel(object):
    """A class representing CANCEL message"""

    def __init__(self):
        self.start_chunk = 0
        self.end_chunk = 0

    def BuildBinaryMessage(self):
        """Build binary version of CANCEL message"""
        wb = bytearray(8)
        pack_into('>II', wb, 0, 
                  self.start_chunk, 
                  self.end_chunk)

        return wb

    def ParseReceivedData(self, data):
        """Parse received data back to the message"""
        contents = unpack('>II', data)
        self.start_chunk = contents[0]
        self.end_chunk = contents[1]
        