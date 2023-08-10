import pympi
import json
from datetime import date
from CoAct_corpus_analysis.speaker_info_encoder import SpeakerInfoEncoder
from CoAct_corpus_analysis.utterance_info import UtteranceInfo

class SpeakerInfo:
    
    """
        This is a speaker class which holds information and functions to track and quiery frequencies of coded labels in ELAN files, 
        such as for Social Action or question type coding.
    """
    
    def __init__(self, dyad, speaker_ID, condition, linked_file):
        self.speaker_ID = speaker_ID
        self.condition = condition
        self.dyad = dyad
        self.linked_file = linked_file
        self.questions = []
        self.responses = []
                  
    def extract_utterances(self, tier):
        
        """
        Extracts all the utterances for the given speaker if the social_action coding file is linked 
        and the given tier tier for the speaker exists.

        Raises:
            ValueError: If none of the linked files correspond to the `social_action` directory.
            KeyError: If the tier doesn't exist for the speaker.

        Returns:
            list: list of UtteranceInfo objects with the start, end and label for each utterance as attributes 
        """
        
        try:
            eaf = pympi.Eaf(self.linked_file)
        except:
            raise ValueError(f'No ELAN file found for {self.dyad}_{self.condition}_{self.speaker_ID}, please provide valid file paths as linked_files.')
        
        #tier will either be Tier_A or Tier_B          
        target_tier = '_'.join([tier, self.speaker_ID])
            
        try:
            intervals = eaf.get_annotation_data_for_tier(target_tier)
        except:
            raise KeyError(f'No {tier} tier found for speaker {self.dyad}, {self.speaker_ID}. \n Make sure this speaker exists')
        
        #for each utterance, get start, end and label for the utterance interval as it is labeled in ELAN
        utterances = []
        for i, iv in enumerate(intervals):
            start, end, label = iv[0], iv[1], iv[-1]
            utterance =  UtteranceInfo(ID=i+1,
                                     interval=(start, end))
            utterances.append(utterance)

        return utterances
                                
                    
    def extract_utterance_overlaps(self, utterances, tierlist):
        
        """
        For each utterance, checks the linked files for temporal overlaps with other intervals from the given tiers.

        Input:
            utterances (list): UtteranceInfo objects
            tierlist (list): tiernames to search for overlaps
        
        Raises:
            KeyError: If any of the tiers in `tierlist` are not found in the linked files.
            Exception: No eaf files were linked when initializing the SpeakerInfo object 

        Returns:
            utterances (list): UtteranceInfo objects now have `overlaps` attribute set
        """
        
        #load all the linked files
        try:
            eaf = pympi.Eaf(self.linked_file)
        except:
            print(f'No ELAN file found for {self.dyad}_{self.condition}_{self.speaker_ID}, please provide valid file paths as linked_files.') 
        
        #for each utterance, get all overlaps from the specified tiers
        for utterance in utterances:
            start = utterance.get_interval()[0]
            end = utterance.get_interval()[-1]
            
            overlaps = {}
            for tier in tierlist:

                    try:
                        #get overlaps in the current utterance window with the tier
                        overlap_intervals = eaf.get_annotation_data_between_times(tier, start, end)
                    except:
                        raise KeyError(f'The target tier {tier} was not found in the linked_files: {self.linked_file}')
                    
                    #sometimes intervals will be immedently after/before each other and share the same start/end point |----|----|
                    #in that case get_annotation_data_between_times() will return BOTH labels from BOTH intervals for these tiers
                    sa_tiers = ['SA_category', 'SA_type', 'Q_type', 'PQ_type']
                    
                    #in that case select only the label with the exact same start/end time as the utterance from the list
                    if any(map(tier.__contains__, sa_tiers)):
                        if len(overlap_intervals) > 1:
                            overlap_intervals = [interval for interval in overlap_intervals if interval[0] == start and interval[1] == end]

                    
                    overlaps[tier] = overlap_intervals
                        #for each utterance set the overlaps attribute to the overlaps we jsut extracted
            utterance.set_overlaps(overlaps)
        
        return utterances
    
    
    def extract_utterance_overlaps_within_time(self, utterances, tierlist, buffer):
        
        """
        For each utterance, checks the linked files for temporal overlaps within a certain time window of the utterance.

        Input:
            utterances (list): UtteranceInfo objects
            tierlist (list): tiernames to search for overlaps
            buffer (int): time window in ms
        
        Raises:
            KeyError: If any of the tiers in `tierlist` are not found in the linked files.
            Exception: No eaf files were linked when initializing the SpeakerInfo object 

        Returns:
            utterances (list): UtteranceInfo objects now have `overlaps` attribute set
        """
        
        try:
            eaf = pympi.Eaf(self.linked_file)
        except:
            print(f'No ELAN file found for {self.dyad}_{self.condition}_{self.speaker_ID}, please provide valid file paths as linked_files.') 
        
        for utterance in utterances:
            start = utterance.get_interval()[0]
            end = utterance.get_interval()[-1]
            
            overlaps = {}
            for tier in tierlist:
                    try:
                        #get overlaps in the current utterance window with the tier
                        overlap_intervals = eaf.get_annotation_data_between_times(tier, start, end)
                    except:
                        raise KeyError(f'The target tier {tier} was not found in the linked_files: {self.linked_file}')
                    
                    overlap_intervals = eaf.get_annotation_data_between_times(tier, start - buffer, end + buffer)
                    overlaps[tier] = overlap_intervals
                        #for each utterance set the overlaps attribute to the overlaps we jsut extracted
            utterance.set_overlaps(overlaps)
            
        return utterances     
    
     
    def save_to_json(self, out_dir):
        
        """
        Saves complete speaker_inof object to a JSON file in the specified directory in the format: Dyad_Condition_Speaker_data.json.
            
        Input:
            out_dir (str): path where to save the files 
        """
        with open(out_dir + f'/{self.dyad}_{self.condition}_{self.speaker_ID}_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, cls=SpeakerInfoEncoder, ensure_ascii=False, indent=4)
                        
                        
    def set_questions(self, utterances):
        self.questions = utterances
    
    def set_responses(self, utterances):
        self.responses = utterances
    
    def get_questions(self):
        return self.questions
    
    def get_responses(self):
        return self.responses
    
    def get_speaker_ID(self):
        return self.speaker_ID
    
    def get_condition(self):
        return self.condition
    
    def get_dyad(self):
        return self.dyad
    
    def get_linked_files(self):
        return self.linked_files   
    
    def get_SA_counter(self):
        return self.SA_counter
        
    def get_Q_type_counter(self):
        return self.Qtype_counter   
    
    def get_FS_counter(self):
        return self.FS_counter 
                
    def get_speakerID(self):
        return self.speaker_ID
    
    def get_SA_types(self):
        return self.SA_types
        
    def get_SA_categories(self):
        return self.SA_cats
        
    def get_polarQ_types(self):
        return self.polarQ_types
    
    def get_Q_types(self):
        return self.Q_types
    
    def get_condition(self):
        return self.condition