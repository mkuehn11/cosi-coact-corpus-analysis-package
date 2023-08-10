from CoAct_corpus_analysis.speaker_info import SpeakerInfo
from CoAct_corpus_analysis.utterance_info import UtteranceInfo
import os
import glob
import json

#working dir
working_dir = os.path.join('.', 'corpus_analysis_package', 'tests')

#output
out_dir = os.path.join('.', 'corpus_analysis_package', 'tests', 'test_output')

#load correct info, this is a file in which the amount of Q/Rs and overlaps was counted manually to test against
with open(os.path.join(working_dir, "test_correct_output.json"), "r") as content:
  correct_output = json.load(content)

#ELAN files
eaf_files = sorted(glob.glob(os.path.join(working_dir, '*.eaf')))

#these are the tiers we want the overlaps for each utterance for
speaker_specific_tiers = ['1_SA_category', '2_SA_category', '1_SA_type', '2_SA_type', 
                'Q_type', 'PQ_type', 'Gaze', 'Blink', 'Squint', 'Eyes-widening', 'Eyebrows', 'Nose-wrinkle', 'Mouth', 'Group']

def save_utterances_per_speaker(speaker = ''):
    
    """
        Extracts all the utterances for the given speaker in each dyad and each condition. 
        Saves the resulting SpeakerInfo object as a JSON file in the output directory. 
    """

    #new SpeakerInfo object
    speaker_info = SpeakerInfo(dyad='01', speaker_ID=speaker, condition='task1', linked_file=eaf_files[0])     

    #get all questions for speaker and check if they're the correct data type and correct amount in the test file
    questions_speaker = speaker_info.extract_utterances(tier = 'Question')
    assert all(isinstance(x, UtteranceInfo) for x in questions_speaker), 'Utterances not generated properly!'
    assert len(questions_speaker) == correct_output[f'n_questions_{speaker}'], f'Incorrect number of questions!'
    
    responses_speaker = speaker_info.extract_utterances(tier = 'Response')
    assert all(isinstance(x, UtteranceInfo) for x in responses_speaker), 'Utterances not generated properly!'
    assert len(responses_speaker) == correct_output[f'n_responses_{speaker}'], f'Incorrect number of responses!'
    
    #the SA and Qtype tiers have _A or _B appended to the tiername
    speaker_tiers = ['_'.join([tiername, speaker]) for tiername in speaker_specific_tiers]

    #get all overlaps of the question with other intervals in the selected tiers
    questions_overlaps = speaker_info.extract_utterance_overlaps(questions_speaker, speaker_tiers)
    responses_overlaps = speaker_info.extract_utterance_overlaps(responses_speaker, speaker_tiers)
    
    #check one question and response each for the correct overlaps
    if speaker == 'A':
        #these are the indices of the selected questions/responses to check
        Qi = 1
        Ri = 12
    if speaker == 'B':
        Qi = 6
        Ri = 9
    
    overlaps_Q = questions_overlaps[Qi -1].get_overlaps() #0 indexing vs. ELAN counting at 1
    overlaps_R = responses_overlaps[Ri -1].get_overlaps()
    values_Q = [val[0][-1] for val in overlaps_Q.values() if val] #for all the overlapping intervals, get only the overlap label, don't care about on/offset time
    values_R = [val[0][-1] for val in overlaps_R.values() if val]
    
    #check if the amount of overlaps is correct (sort in case the order is different)
    assert sorted(values_Q) == sorted(correct_output[f'n_overlaps_{speaker}Q{Qi}']), f"Incorrect extraction for the Question_A tier. Amount of overlaps should be {correct_output[f'n_overlaps_{speaker}Q{Qi}']} but is {values_Q}"
    assert sorted(values_R) == sorted(correct_output[f'n_overlaps_{speaker}R{Ri}']), f"Incorrect extraction for the Response_A tier. Amount of overlaps should be {correct_output[f'n_overlaps_{speaker}R{Ri}']} but is {values_R}"

    speaker_info.set_questions(questions_overlaps)
    speaker_info.set_responses(responses_overlaps)
    
    assert speaker_info.questions, "Questions not set!"
    assert speaker_info.responses, "Responses not set!"
    
    speaker_info.save_to_json(out_dir) #write
    assert os.path.isfile(os.path.join(out_dir, '01_task1_A_data.json')), "File for speaker A not written!"
    assert os.path.isfile(os.path.join(out_dir, '01_task1_B_data.json')), "File for speaker B not written!"

save_utterances_per_speaker(speaker='A')
save_utterances_per_speaker(speaker='B')

