import pympi
import json
from datetime import date
from CoAct_question_analysis.speaker_info_encoder import SpeakerInfoEncoder
from CoAct_question_analysis.question_info import QuestionInfo

class SpeakerInfo:
    
    """
        This is a speaker class which holds information and functions to track and quiery frequencies of coded labels in ELAN files, 
        such as for Social Action or Question type coding.
    """
    
    def __init__(self, dyad, speaker_ID, condition, linked_files):
        self.speaker_ID = speaker_ID
        self.condition = condition
        self.dyad = dyad
        self.linked_files = linked_files
        self.questions = []
        
        #all possible labels for Social Action Types and Categories
        self.SA_types = ['FS','NFS','RE','RCI','PH','PU','CHECK','SI','CC','ALIGN','Align-pref','PI','SCA','JH','CH','COR','WARN','AS',
            'ER','COMP','DIAG','DIAP','PROP','OFF','SUGG','ACTD', 'INV','NR','SURP','DSI','BCK','OL','SD','RS','TI','ELAB','PRE','FRAME']
        self.SA_cats = ['RI', 'OIR', 'MU','EAS','PA','AP','NDOS','SIMCA']
        self.SAs = self.SA_cats + self.SA_types + ['UNKNOWN'] #UNKNOWN is for labels that are not within the standard language of the tier (i.e. empty)
        
        #all possible question types
        self.polarQ_types =  ['declarative', 'tag', 'interrogative', 'non-clausal', 'NA']
        self.Q_types = ['polar', 'content', 'alternative']
        self.allQ_types = self.Q_types + self.polarQ_types + ['UNKNOWN']
        
        #all possible facial signals
        self.facial_signals = ['away', 'blink','squint', 'wider', 'raised', 'unilateral-raised', 'lowered', 'frown', 'frown-raised', 
                               'frown+unilateral-raised', 'wrinkle', 'lips pressed together', 'one/both corners pulled back', 
                               'one/both corners pulled down', 'lips pursed', 'smile', 'one-side smile', 'single up', 'single down', 
                               'biphasic up+down', 'biphasic down+up', 'multiple up+down', 'multiple down+up', 'single left', 'single right', 
                               'biphasic left+right', 'biphasic right+left', 'multiple left+right', 'multiple right+left', 'single left', 
                               'single right', 'biphasic left+right', 'biphasic right+left', 'multiple left+right', 'multiple right+left', 
                               'single front', 'single back', 'biphasic front+back', 'biphasic back+front', 'multiple front+back', 
                               'multiple back+front', 'not-face', 'thinking-face', 'surprise-face', '?', 'UNKNOWN']
        
                
        #set up empty counter for the coding schemes
        self.SA_counter = {}
        for SA in self.SAs:
             self.SA_counter[SA] = 0 # default value for all counters
             
        self.Qtype_counter = {}
        for Qtype in self.allQ_types:
             self.Qtype_counter[Qtype] = 0 # default value for all counters
             
        self.FS_counter = {}
        for FS in self.facial_signals:
             self.FS_counter[FS] = 0 # default value for all counters
             
        self.secondary_SA_counter = {}
        for SA in self.SAs:
             self.secondary_SA_counter[SA] = 0 # default value for all counters
    
    def extract_questions(self):
        
        """
        Extracts all the questions for the given speaker if the social_action coding file is linked 
        and the Question tier for the speaker exists.

        Raises:
            ValueError: If none of the linked files correspond to the `social_action` directory.
            KeyError: If the "Question_A/B" tier doesn't exist for the speaker.

        Returns:
            list: list of QuestionInfo objects with the start, end and label for each question as attributes 
        """
        #get the correct coding scheme from the linked files
        SA_file = [file for file in self.linked_files if 'social_action' in file]
        try:
            eaf = pympi.Eaf(SA_file[0])
        except:
            raise ValueError(f'No ELAN file found for {self.dyad}_{self.condition}_{self.speaker_ID}, please provide valid file paths as linked_files.')
        
        #tier will either be Question_A or Question_B          
        target_tier = '_'.join(['Question', self.speaker_ID])
            
        try:
            question_intervals  = eaf.get_annotation_data_for_tier(target_tier)
        except:
            raise KeyError(f'No question tier found for speaker {self.dyad}, {self.speaker_ID}. \n Make sure this speaker exists')
        
        #for each question, get start, end and label for the question interval as it is labeled in ELAN
        questions = []
        for i, question in enumerate(question_intervals):
            start, end, label = question[0], question[1], question[-1]
            question =  QuestionInfo(ID=i+1,
                                     interval=(start, end),
                                     transcript=label)
            questions.append(question)
            
        return questions
                                
                    
                    
    def extract_question_overlaps(self, questions, tierlist):
        
        """
        For each question, checks the linked files for temporal overlaps with other intervals from the given tiers.

        Input:
            questions (list): QuestionInfo objects
            tierlist (list): tiernames to search for overlaps
        
        Raises:
            KeyError: If any of the tiers in `tierlist` are not found in the linked files.
            Exception: No eaf files were linked when initializing the SpeakerInfo object 

        Returns:
            questions (list): QuestionInfo objects now have `overlaps` attribute set
        """
        
        #laod all the linked files
        eafs = []
        try:
            for file in self.linked_files:
                eaf = pympi.Eaf(file)
                eafs.append(eaf)
        except:
            print(f'No ELAN file found for {file}, please provide valid file paths as linked_files.') 
        
        #for each question, get all overlaps from the specified tiers
        for question in questions:
            start = question.get_interval()[0]
            end = question.get_interval()[-1]
            
            overlaps = {}
            for tier in tierlist:
                    #since most of the tiers have a name extension with the initals of the annotator it's difficult do match directly
                    target_eaf = None
                    for eaf in eafs:
                        #find matching tiers with the keyword of the tier
                        matching_tier = [tiername for tiername in eaf.get_tier_names() if tier in tiername]
                        if len(matching_tier) > 1:
                            #if multiple tiers are found (i.e. multiple speakers) take only the direct match
                            matching_tier = [match for match in matching_tier if tier == match] #this is not foolproof and only works as long as all tiernames are fairly unique
                        if matching_tier:
                            target_eaf = eaf
                            break
                    if target_eaf == None:
                        raise KeyError(f'The target tier {tier} was not found in any of the linked_files: {self.linked_files}')
                    
                    #get overlaps in the current question window with the tier
                    overlap_intervals = target_eaf.get_annotation_data_between_times(matching_tier[0], start, end)
                    
                    #sometimes questions will be immedently after/before each other and share the same start/end point |----|----|
                    #in that case get_annotation_data_between_times() will return BOTH labels from BOTH questions for these tiers
                    speaker_specific_tiers = ['SA_category', 'SA_type', 'Q_type', 'PQ_type']
                    
                    #in that case select only the label with the exact same start/end time as the question from the list
                    if any(map(matching_tier[0].__contains__, speaker_specific_tiers)):
                        if len(overlap_intervals) > 1:
                            overlap_intervals = [interval for interval in overlap_intervals if interval[0] == start and interval[1] == end]

                    
                    overlaps[tier] = overlap_intervals
            
            #for each question set the overlaps attribute to the overlaps we jsut extracted
            question.set_overlaps(overlaps)
        
        return questions
    
    
    def extract_question_overlaps_within_time(self, questions, tierlist, buffer):
        
        """
        For each question, checks the linked files for temporal overlaps within a certain time window of the question.

        Input:
            questions (list): QuestionInfo objects
            tierlist (list): tiernames to search for overlaps
            buffer (int): time window in ms
        
        Raises:
            KeyError: If any of the tiers in `tierlist` are not found in the linked files.
            Exception: No eaf files were linked when initializing the SpeakerInfo object 

        Returns:
            questions (list): QuestionInfo objects now have `overlaps` attribute set
        """
        
        eafs = []
        try:
            for file in self.linked_files:
                eaf = pympi.Eaf(file)
                eafs.append(eaf)
        except:
            print(f'No ELAN file found for {file}, please provide valid file paths as linked_files.') 
        
        for question in questions:
            start = question.get_interval()[0]
            end = question.get_interval()[-1]
            
            overlaps = {}
            for tier in tierlist:
                    #since most of the tiers have a name extension with the initals of the annotator it's difficult do match directly
                    target_eaf = None
                    for eaf in eafs:
                        #find matching tiers with the keyword of the tier
                        matching_tier = [tiername for tiername in eaf.get_tier_names() if tier in tiername]
                        if len(matching_tier) > 1:
                            #if multiple tiers are found (i.e. multiple speakers) take only the direct match
                            matching_tier = [match for match in matching_tier if tier == match] #this is not foolproof and only works as long as all tiernames are fairly unique
                        if matching_tier:
                            target_eaf = eaf
                            break
                    if target_eaf == None:
                        raise KeyError(f'The target tier {tier} was not found in any of the linked_files: {self.linked_files}')
                    
                    overlap_intervals = target_eaf.get_annotation_data_between_times(matching_tier[0], start - buffer, end + buffer)
                    overlaps[tier] = overlap_intervals
            
            question.set_overlaps(overlaps)
        
        return questions     
    
    
    #to increase counts, simply pass the label and count, don't have to specify whether SA or Qtype etc
    def find_counter(self, label):
        all_counters = [self.SA_counter, self.Qtype_counter, self.FS_counter]
        
        target_counter = None
        for counter_dict in all_counters:
            for key in counter_dict.keys():
                if label == key:
                    target_counter = counter_dict
                    return target_counter
                
        if target_counter == None:
            current_date = str(date.today())
            f = open('error_log_CoAct.txt', 'a') #log these so files with empty labels are tracked and can be fixed
            f.write(f'\n {current_date} \n An unknown label was found for file {self.dyad}, spekaer {self.speaker_ID} for label {label}. \n')
            f.close()
                    
            raise KeyError(f'Label {label} is unknown for Social Actions, Question type or Facial Signals.')


    
    #set frequency for one single label  
    def set_freq(self, label, count):
        counter = self.find_counter(label)
        counter[label] = count
    
    #set frequency from a {label: value} dictionary
    def set_freq_from_dict(self, count_dict):
        for key, value in count_dict.items():
            self.set_freq(key, value)
    
       
    def calculate_frequencies_from_questions(self):
        """
        Calculates frequencies by counting all questions and question overlaps and updates the SpeakerInfo attributes.

        Raises:
            ValueError: If questions are not set.
        """
        
        if not self.questions:
            raise ValueError(f"Questions must be set using extract_questions() and extract_question_overlaps()!")
        
        for question in self.questions:
            overlaps = question.get_overlaps()
            for tier, values in overlaps.items():
                labels = [label[-1] for label in values]
                for label in labels:
                    if '2_SA' in tier:
                        counter = self.secondary_SA_counter
                        counter[label] += 1
                        
                    if label == '': #if the label is empty the counter has to be set manually
                        current_date = str(date.today())
                        f = open('error_log_CoAct.txt', 'a') #log these so files with empty labels are tracked and can be fixed
                        f.write(f'\n {current_date} \n An empty label was found for file {self.dyad}, speaker {self.speaker_ID} in tier {tier}. \n')
                        f.close()
                        
                        if '1_SA_' in tier:
                            self.SA_counter['UNKNOWN'] += 1
                        elif '2_SA_' in tier:
                            self.secondary_SA_counter['UNKNOWN'] += 1
                        elif 'Q_' in tier:
                            self.Qtype_counter['UNKNOWN'] += 1
                        else:
                            self.FS_counter['UNKNOWN'] += 1
                    else:
                        counter = self.find_counter(label)
                        counter[label] += 1

    
    
     
    def save_to_json(self, out_dir):
        
        """
        Saves complete speaker_inof object to a JSON file in the specified directory in the format: Dyad_Condition_Speaker_data.json.
            
        Input:
            out_dir (str): path where to save the files 
        """
        with open(out_dir + f'/{self.dyad}_{self.condition}_{self.speaker_ID}_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, cls=SpeakerInfoEncoder, ensure_ascii=False, indent=4)
                        
                        
    def set_questions(self, questions):
        self.questions = questions
        
    def set_SA_counter(self, counter):
        self.SA_counter = counter
        
    def set_secondary_SA_counter(self, counter):
        self.secondary_SA_counter = counter
        
    def set_FS_counter(self, counter):
        self.FS_counter = counter
        
    def set_Qtype_counter(self, counter):
        self.Qtype_counter = counter    
    
    def get_freq(self, label):
        counter = self.find_counter(label)
        return counter[label]
    
    def get_questions(self):
        return self.questions
    
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