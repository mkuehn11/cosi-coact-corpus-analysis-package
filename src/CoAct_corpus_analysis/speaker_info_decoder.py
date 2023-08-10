import json
from CoAct_corpus_analysis.speaker_info import SpeakerInfo
from CoAct_corpus_analysis.utterance_info import UtteranceInfo


"""
    JSON.load() doesn't read the speaker object in as a dictionary, not SpeakerInfo and UtteranceInfo objects.
    This function takes in a file path to a json file and returns the SpeakerInfo object.
Input:
    file: str, path to JSON file

Returns:
    speaker_info: SpeakerInfo object
"""

def decode_utterances(speaker_info_file, utterance_type):
    #loop over utterance list to create UtteranceInfo objects and set them for the SpeakerInfo object
    utterance_objs = []
    for i, utt in enumerate(speaker_info_file[utterance_type]):
        
        utterance_info_obj = UtteranceInfo(ID=i+1, 
                                        interval=tuple(utt[0]))
        utterance_info_obj.set_overlaps(utt[1])
        utterance_objs.append(utterance_info_obj)
    
    return utterance_objs


def load_speaker_from_json(file):
    
    with open(file, 'r') as f:
        speaker_info_file = json.load(f)
    
    #initialize object with info from dict 
    speaker_info_obj = SpeakerInfo(dyad = speaker_info_file['dyad'], 
                                    speaker_ID = speaker_info_file['speaker_ID'],
                                    condition = speaker_info_file['condition'],
                                    linked_file = speaker_info_file['linked_file'])
    
    
    question_objs = decode_utterances(speaker_info_file, 'questions')
    response_objs = decode_utterances(speaker_info_file, 'responses')
        
    speaker_info_obj.set_questions(question_objs)
    speaker_info_obj.set_responses(response_objs)
        
    return speaker_info_obj