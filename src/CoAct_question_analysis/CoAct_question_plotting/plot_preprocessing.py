import numpy as np
import pandas as pd
from ast import literal_eval

def melt_and_explode_column(df, value_name, literal_eval_for_col = True):
    ''' summary'''
    
    #melt the dataframe - stacks all columns vertically
    melt_df = pd.melt(df, value_name=value_name)
    
    #literal eval will read in lists/tuples as the correct dtypes
    if literal_eval_for_col:
         melt_df[value_name] = melt_df[value_name].apply(literal_eval)
    
    #if there is a list/tuple in a cell, explode will split the list and duplicate the rows  
    explode_df = melt_df.explode(value_name)
    
    return explode_df


def get_percentage_column(df, drop_zeros = True):
    ''' summary'''
    prct_cols = [col for col in df if 'prct' in col] #all the percentages for each tier

    prct_df = melt_and_explode_column(df = pd.concat([df[prct_cols]]), 
                                      value_name='overlap_prct', 
                                      literal_eval_for_col=True) #get one column with all the individual percentages stacked
    
    if drop_zeros:
        prct_df = prct_df[prct_df['overlap_prct'] != 0]

    #return only the percentages column
    return prct_df['overlap_prct']
    
    
     
def get_label_column(df, drop_zeros = True):
    ''' summary'''
    label_cols = [col for col in df if 'label' in col] #all the labels for each tier
    
    label_df = melt_and_explode_column(df = pd.concat([df[label_cols]]), 
                                        value_name='overlap_label', 
                                        literal_eval_for_col=True) #get one column with all the individual labels stacked
    
    if drop_zeros:
        label_df = label_df[label_df['overlap_label'] != '']
    
    
    #return only the labels column
    return label_df['overlap_label']
    


def get_question_timings(df, timing_cols):
    #start and end of original question
    question_timing = pd.DataFrame(np.tile(df['on_offset'], (1,len(timing_cols))))
    question_timing = pd.melt(question_timing, value_name='question_on_offset')
    
    return question_timing

def get_timing_df(df):
    ''' summary'''
    
    timing_cols = [col for col in df if 'start_end' in col] #all the timings of the overlapping labels for each tier
    
    #get the on_offset information of the questionas well as the overlapping label
    question_timings = get_question_timings(df, timing_cols)
    
    timing_df = pd.melt(pd.concat([df[timing_cols]]), var_name = 'tier', value_name='label_on_offset')
    timing_df['tier'] = timing_df['tier'].str.split('_').str[0] #isolate only the actual tiername without appendix
    timing_df['label_on_offset'] = timing_df['label_on_offset'].apply(literal_eval)
    
    #first add the question_on_offset column to the timing_df so those rows are duplicated as well during df.explode()
    timing_df['question_on_offset'] = question_timings['question_on_offset'].apply(literal_eval)
    timing_df = timing_df.explode('label_on_offset')
    
    #return full df
    return timing_df

def exclude_blinks(df, out_file):
    '''summary'''
    
    #filter blink durations
    short_blinks = df.loc[(df['tier'] == 'Blink') & (df['label_dur'] < 410)]
    short_blinks.to_csv(out_file)

    #exclude short blinks from df
    filtered_df = df[~df.index.isin(short_blinks.index)]
    
    return filtered_df


def add_onset_difference(df):
    
    '''sumamry'''
    
    #split the tuple columns of on_offset into separate start and end columns
    label_on_offset = pd.DataFrame(df['label_on_offset'].tolist(), columns=['label_start', 'label_end'])
    question_on_offset = pd.DataFrame(df['question_on_offset'].tolist(), columns=['question_start', 'question_end'])

    #keep only the split columns
    df.reset_index(inplace=True, drop=True)
    split_timing_df = pd.concat([df, label_on_offset, question_on_offset], axis = 1)
    
    #add columns for duration and relative onset
    split_timing_df['label_dur'] = split_timing_df['label_end'] - split_timing_df['label_start']
    split_timing_df['onset_difference'] =  split_timing_df['label_start'] - split_timing_df['question_start']
    
    return split_timing_df