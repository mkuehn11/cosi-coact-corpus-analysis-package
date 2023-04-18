## Question analysis CoAct Corpus

Analysis of questions in the CoAct corpus. The goal is to extract all questions with a social action assigned to it and check the frequency of those labels, the associated transcript and overlaps with other question types and facial signals.

The output is JSON and .csv files containing all the questions from each speaker in each dyad along with the associated social action and question type labels as well as the amount of overlap with other types of (facial) signals.

#### Corpus

The corpus is structured in `dyads`, speakers and `utterances`.  A dyad is a conversation between two speakers, and indicated by the number prepended to all files (`01-99`). Different speakers are indicated using `A` and `B` .  Utterances are either questions or responses uttered by speaker A or B.

Questions annotated in ELAN, which allows for precise time annotations and stores those annotations in XML like `.eaf` files. Those files are readable and modifyable using the `pympi` Python package.

Different levels of information are annotated in different `tiers` in ELAN. A tier contains multiple `interval annotations`, which each have a `start time`, `end time` and `label` associated with it. One time interval can have multiple overlapping annotations in different tiers. Each question, which is annotated in the tiers `Questions_A` and `Questions_B` will have additional information assigned to it in other tiers. Those tiers are:

* `Q_type` (question type)
* `PQ_type` (polar question type)
* `1_SA_category` (primary social action category)
* `2_SA_category` (secondary social action category)
* `1_SA_type` (primary social action type)
* `2_SA_type` (secondary social action type)

These intervals overlap exactly and will have the same start and end time as the question.

Additionally to the social action coding, `facial signals` have been annotated as well. These signals are losely grouped into different tiers for different parts of the face or head, the individual annotations may overlap with the question or other facial signals or occur individually. The facial signal tiers are:

* `Gaze`
* `Blink`
* `Squint`
* `Eyes-widening`
* `Eyebrows`
* `Nose-wrinkle`
* `Mouth`
* `Group`

#### SpeakerInfo and QuestionInfo classes

To efficiently analyze the question in the corpus, the data structures `SpeakerInfo` and `QuestionInfo` hold all the information that is coded in ELAN. The classes represent the speaker and utterance level respectively.

A `QuestionInfo` object contains the question `ID` (number of the question in the ELAN file), the `interval` (start and end time in ms), the `transcript` (clear text transcript of the question if available) and a placeholder for `overlaps` with other annotations in the same interval. As well as a number of getters and setters to access these attributes.

The `SpeakerInfo` class contains information about the `file`, `dyad`, `task` and `speaker_ID`, but also holds a list of `QuestionInfo` objects, frequency `counters`, as well as class functions to extract questions and question overlaps:

* `extract_questions()`
  * checks all the files which are linked to this speaker and extracts all question intervals from the ELAN files
* `extract_question_overlaps(questions, tierlist)`
  * loops over all the questions and finds all annotations from the specified tierlist which have any temporal overlap with the question interval
* `extract_question_overlaps_within_time(questions, tierlist, buffer)`
  * similar to the above, extracts all temporal overlaps within a given time window of the question, i.e. +- 200ms
* `calculate_frequencies_from_questions()`
  * this updates all the counters of the `SpeakerInfo` object with the absolute frequencies of each social action, question type or facial signals
* `save_to_json()`
  * saves the object to a JSON file using the `speaker_info_encoder.py` this amkes it easier to read in information for future data analyses without having to iterate over ELAN files every time or hold all speaker in the working memory

#### Files & Analyses

The class files and the scripts to extract and plot all questions/social actions are at the top level:

##### Scripts

* `speaker_info.py`
  * SpeakerInfo class
* `question_info.py`
  * QuestionInfo class
* `speaker_info_encoder.py`
  * encoder to save `SpeakerInfo` objects to JSON files
* `speaker_info_decoder.py`
  * decoder to read in JSON files as `SpeakerInfo` objects
* `extract_questions.py`
  * loops over all ELAN files in the facial signal and social action coding directories for all tasks and extracts all questions for each speaker, including overlaps with other tiers and saves these objects as JSON files in the `speaker_info` directory.
* `extract_all_SA_categories.py`
  * reads in and loops over all the JSON files and extracts all the questions belonging to one of the social action categories `['OIR', 'RI', 'MU', 'EAS', 'PA', 'NDOS', 'SIMCA']` and saves these questions in .csv files in the `/analyses/question_csvs/ `directory
* `extract_all_SA_types.py` reads in and loops over all the JSON files and extracts all the questions belonging to one of the social action types `['FS','NFS','RE','RCI','PH','PU','CHECK','SI','CC','ALIGN','Align-pref','PI','SCA', 'JH','CH','COR','WARN','AS','ER','COMP','DIAG','DIAP','PROP','OFF','SUGG','ACTD', 'INV','NR','SURP','DSI','BCK','OL','SD','RS','TI','ELAB','PRE','FRAME']` and saves these questions in .csv files in the `/aalyses/question_csvs/ `directory
* `generate_FS_matrices.py`
  * uses the .csv files from the `/analyses/question_csvs/ ` directory and generates confusion matrices of which facial signals occur with each other at the same time
* `plot_SA_questions.py`
  * generates a number of plots using frequency statistics of social actions and saves them in the `/analyses/plots/` directory
* `plot_facial_signals.py`
  * generates a number of plots using frequency statistics of facial signals and saves them in the `/analyses/plots/` directory

##### Directories

* `analyses`
  * place for scripts and materials for specific research questions targeting specific Social Actions/Facial Signals
  * contains csvs for question/facial signal frequencies
  * contains plotting scripts
* `misc`
  * handy documents such as coding abbreviations, tiernames, dyad names
* `speaker_info`
  * directory with all the speaker JSON files containing all information about questions and overlapping intervals

##### How to run

* `requirements.txt` can be used to create a virtual env with all the listed dependencies, or they can be installed manually
* the JSON files in speaker_info are extracted using the `extract_questions.py` script. If new labels are annotated or more tiers included, run the script again with the respective tiers
* create a new directory in `analyses` for specific research questions, statistical analyses or plotting
* use the `load_speaker_from_json` function in the `speaker_info_decoder` to read in JSON files as class objects for further analyses


##### Error log

* the `error_log_CoAct.txt` tracks empty/missing labels from tiers so they can be tracked and added later
