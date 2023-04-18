import json

"""
Encoder that can be passed to json.dump() under the `cls` flag.

Returns:
    SpeakerInfo.attributes: which can be written to the json file.
"""

class SpeakerInfoEncoder(json.JSONEncoder):
    def default(self, speaker_obj):
        return [speaker_obj.get_interval(),
        speaker_obj.get_transcript(),
        speaker_obj.get_overlaps()
        ]