import hashlib

class CleftObj:

    def __init__(self):

        # Physical filepath
        self.CleftFile = ''
        
        # Name of object in PyMOL
        self.CleftName = ''

        # Partition flag
        self.Partition = False
        # Reference to a cleft object
        self.PartitionParent = None
        
        # Allows to not calculate volume twice
        self.Volume = 0.000

        self.Index = 0

    ''' ==================================================================================
    FUNCTION Set_CleftMD5: Provides a unique ID to a cleft file
    ================================================================================== '''
    def Set_CleftMD5(self):

        md5 = hashlib.md5()
        md5.update(self.CleftFile)
        
        self.CleftMD5 = md5.digest()
