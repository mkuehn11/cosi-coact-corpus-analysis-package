## Analysis CoAct Corpus


## Installation

* install with `pip install path/to/corpus_analysis_package`
* `requirements.txt` can be used to create a virtual env with all the listed dependencies, or they can be installed manually

## Usage


* Initialize a new SpeakerInfo object by providing the dyad number, speaker ID (A/B), the condition (task1, task2, task3) and the corresponding `.eaf` file
``` 
    speaker_info = SpeakerInfo(dyad=dyad, speaker_ID=speaker, condition=condition, linked_file=file)     
``` 

* Use the class function to extract questions and responses from the `eaf` files
```
    questions_speaker = speaker_info.extract_utterances(tier = 'Question')
    responses_speaker = speaker_info.extract_utterances(tier = 'Response')
```
    speaker_tiers = ['_'.join([tiername, speaker]) for tiername in speaker_specific_tiers]
    
* Get the facial signal overlaps of each question/response by specifying the desired tiers

```
    questions_overlaps = speaker_info.extract_utterance_overlaps(questions_speaker, ['Gaze_A', 'Gaze_B', 'Nose-wrinkle_A', 'Nose-wrinkle_B'])
    responses_overlaps = speaker_info.extract_utterance_overlaps(responses_speaker, ['non-rep_form_A', 'non-rep_form_B'])
```

* Use the class setters to assign questions/responses to the SpeakerInfo class object 

```
    speaker_info.set_questions(questions_overlaps)
    speaker_info.set_responses(responses_overlaps)
```

* Write the class object to json files

``` 
    speaker_info.save_to_json(out_dir)
```

## Documentation

Analysis of utterances in the CoAct corpus. The goal is to extract all utterances with a social action assigned to it and check the frequency of those labels, the associated transcript and overlaps with other utterance types and facial signals.

The output is JSON and .csv files containing all the utterances from each speaker in each dyad along with the associated social action and utterance type labels as well as the amount of overlap with other types of (facial) signals.

#### Corpus

The corpus is structured in `dyads`, speakers and `utterances`.  A dyad is a conversation between two speakers, and indicated by the number prepended to all files (`01-99`). Different speakers are indicated using `A` and `B` .  Utterances are either questions or responses by speaker A or B.

Utterances are annotated in ELAN, which allows for precise time annotations and stores those annotations in XML like `.eaf` files. Those files are readable and modifyable using the `pympi` Python package. The goal of this package is to extract relevant information from the `.eaf` files and store that information in a convenient format (`.json` files).

Different levels of information are annotated in different `tiers` in ELAN. A tier contains multiple `interval annotations`, which each have a `start time`, `end time` and `label` associated with it. One time interval can have multiple overlapping annotations in different tiers. Each utterance, which is annotated in the tiers `Question_A` and `Question_B` and `Response_A` and `Response_B` will have additional information assigned to it in other tiers. Those tiers are:

* `Q_type` (utterance type)
* `PQ_type` (polar utterance type)
* `1_SA_category` (primary social action category)
* `2_SA_category` (secondary social action category)
* `1_SA_type` (primary social action type)
* `2_SA_type` (secondary social action type)

These intervals overlap exactly and will have the same start and end time as the utterance.

Additionally to the social action coding, `facial signals` and `gestures` have been annotated as well. These signals are losely grouped into different tiers for different parts of the face or head, the individual annotations may overlap with the utterance or other facial signals or occur individually. The facial signal tiers are:

* `Gaze`
* `Blink`
* `Squint`
* `Eyes-widening`
* `Eyebrows`
* `Nose-wrinkle`
* `Mouth`
* `Group`
* `non-rep gestures`

#### SpeakerInfo and UtteranceInfo classes

To efficiently analyze the utterances in the corpus, the data structures `SpeakerInfo` and `UtteranceInfo` hold all the information that is coded in ELAN. The classes represent the `speaker` and `utterance` level respectively.

A `UtteranceInfo` object contains the utterance `ID` (number of the utterance in the ELAN file), the `interval` (start and end time in ms) and a placeholder for `overlaps` with other annotations in the same interval. As well as a number of getters and setters to access these attributes.

The `SpeakerInfo` class contains information about the `file`, `dyad`, `task` and `speaker_ID`, but also holds a list of `UtteranceInfo` objects, as well as class functions to extract utterances and utterance overlaps:

* `extract_utterances()`
  * checks the `eaf` files which are linked to this speaker and extracts all utterance intervals from the ELAN files
* `extract_utterance_overlaps(utterances, tierlist)`
  * loops over all the utterances and finds all annotations from the specified tierlist which have any temporal overlap with the utterance interval
* `extract_utterance_overlaps_within_time(utterances, tierlist, buffer)`
  * similar to the above, extracts all temporal overlaps within a given time window of the utterance, i.e. +- 200ms
* `save_to_json()`
  * saves the object to a JSON file using the `speaker_info_encoder.py` this amkes it easier to read in information for future data analyses without having to iterate over ELAN files every time or hold all speaker in the working memory

#### Files

The package consists of the `speaker_info.py` and `utterance_info.py` classes as well as the `speaker_info_decoder.py` and `speaker_info_encoder.py` which serialized/deserializes class objects to and from json files.

## CoAct_corpus_plotting submodule

This submodule provides pre-processing and plotting functions to visualize timing and frequency information based on dataframes which can be constructed from the json files.

* `plot_preprocessing.py`
  * Prepares datframes for plotting, the main purpose is to disentangle multiple temporal overlaps between i.e. facial signals and questions and turning them into separate observations.
* `SA_plotting.py`
  * Plotting functions for social actions, including frequency distributions, overlaps with facial signals and temporal distributions
* `FS_plotting.py`
  * Plotting functions for facial signals, including co-occurrence matrices.