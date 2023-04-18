import json
from CoAct_question_analysis.speaker_info import SpeakerInfo
from CoAct_question_analysis.question_info import QuestionInfo


"""
    JSON.load() doesn't reads the speaker object in as a dictionary, not SpeakerInfo and QuestionInfo objects.
    This function takes in a file path to a json file and returns the SpeakerInfo object.
Input:
    file: str, path to JSON file

Returns:
    speaker_info: SpeakerInfo object
"""

def load_speaker_from_json(file):
    
    with open(file, 'r') as f:
        speaker_info_file = json.load(f)
    
    #initialize object with info from dict 
    speaker_info_obj = SpeakerInfo(dyad = speaker_info_file['dyad'], 
                                    speaker_ID = speaker_info_file['speaker_ID'],
                                    condition = speaker_info_file['condition'],
                                    linked_files = speaker_info_file['linked_files'])
    
    #set the counters so they can be accessed using get() from the SpeakerInfo object
    speaker_info_obj.set_FS_counter(speaker_info_file['FS_counter'])
    speaker_info_obj.set_Qtype_counter(speaker_info_file['Qtype_counter'])
    speaker_info_obj.set_SA_counter(speaker_info_file['SA_counter'])
    speaker_info_obj.set_secondary_SA_counter(speaker_info_file['secondary_SA_counter'])
    
    #loop over question list to create QuestionInfo objects and set them for the SpeakerInfo object
    question_objs = []
    for i, question in enumerate(speaker_info_file['questions']):
        
        question_info_obj = QuestionInfo(ID=i+1, 
                                        interval=tuple(question[0]), 
                                        transcript=question[1])
        question_info_obj.set_overlaps(question[2])
        question_objs.append(question_info_obj)
        
    speaker_info_obj.set_questions(question_objs)
        
    return speaker_info_obj