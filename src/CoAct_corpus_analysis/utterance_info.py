class UtteranceInfo:
    
    """
        This is an utterane class which holds information about the onset, offset, text transcript and overlaps of each utterance (i.e. questions or responses).
    """
    
    def __init__(self, ID, interval):
        self.ID = ID                                #index (as in ELAN, starting at 1)
        self.interval = interval                    #start, end in ms, tuple
        self.overlaps = {}                          #overlaps with other tiers


    def get_ID(self):
        return self.ID
    
    def get_interval(self):
        return self.interval
    
    def get_start(self):
        return self.interval[0]
    
    def get_end(self):
        return self.interval[-1]
    
    def get_duration(self):
        return self.interval[-1] - self.interval[0]
    
    def get_transcript(self):
        return self.transcript
    
    def get_overlaps(self):
        return self.overlaps
    
    def set_overlaps(self, overlaps):
        self.overlaps = overlaps
    
    def set_ID(self, ID):
        self.ID = ID
    
    def set_interval(self, interval):
        self.interval = interval
    
    def set_transcript(self, transcript):
        self.transcript = transcript