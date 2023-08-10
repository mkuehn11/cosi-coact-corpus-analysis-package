import os
import glob
import json
from CoAct_corpus_analysis.speaker_info import SpeakerInfo
from CoAct_corpus_analysis.utterance_info import UtteranceInfo
from CoAct_corpus_analysis.speaker_info_decoder import load_speaker_from_json


test_output_dir = os.path.join('/data', 'workspaces', 'cosi','workspaces','cosi-coact',
                               'working_data', 'corpus', 'CoAct_corpus_analysis', 'Michelle',
                               'CoAct_corpus_analysis', 'corpus_analysis_package', 'tests', 'test_output')
test_files = glob.glob(os.path.join(test_output_dir, '*.json'))

for test_file in test_files:
    
    speaker_info = load_speaker_from_json(file = test_file)
    assert isinstance(speaker_info, SpeakerInfo), 'Object not decoded as correct type!'
    assert all(isinstance(x, UtteranceInfo) for x in speaker_info.get_questions()), 'Questions not decoded properly!'
    assert all(isinstance(x, UtteranceInfo) for x in speaker_info.get_responses()), 'Responses not decoded properly!'