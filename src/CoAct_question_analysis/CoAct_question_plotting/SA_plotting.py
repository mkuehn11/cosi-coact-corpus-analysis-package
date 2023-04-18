import matplotlib.pyplot as plt
import seaborn as sns 
import pandas as pd
import numpy as np
import os
from collections import Counter

def plot_frequency(question_df, tier, sa, out_dir, relative=False):
    
    counter = Counter(question_df[tier])
    
    if relative:
        counter = {i: counter[i] / len(question_df[tier]) * 100.0 for i in counter}
        out_file = os.path.join(out_dir, f'{sa}_{tier}_relative_frequency.png')  
    else:
        out_file = os.path.join(out_dir, f'{sa}_{tier}_absolute_frequency.png')
        
    counter = {k: counter[k] for k in counter if type(k) is str} #exclude nan values
    df = pd.DataFrame({tier: counter.keys(), 'Count': counter.values()}, index = np.arange(0, len(counter.keys()), 1))
        
    ax = sns.barplot(data = df, x = tier, y = 'Count')
    
    if relative:      
        ax.bar_label(ax.containers[0],  labels=[f'{x:,.2f}' for x in ax.containers[0].datavalues])
        ax.set_ylabel('Frequency (%)')
    else:
        ax.bar_label(ax.containers[0])
        ax.set_ylabel('Count')
        
    ax.set_title(f'{tier} frequency of {sa} questions (n = {len(question_df)})')
    ax.get_figure().savefig(out_file)
    plt.close()


def plot_relative_onset(plotting_df, sa, out_dir):
    fig, axs = plt.subplots(4, 2, figsize=(15,10))

    tiers = ['Gaze', 'Blink', 'Squint', 'Eyes-widening', 'Eyebrows', 'Nose-wrinkle', 'Mouth', 'Group']
    for i, ax in enumerate(axs.flatten()):
        f = plotting_df.loc[plotting_df['tier'] == tiers[i]]
        sns.kdeplot(data=f, x="onset_difference", hue="overlap_label", fill=True, alpha=.5, ax = ax)
        ax.axvline(x = 0, ls = ':', color = 'gray', alpha = .8)
        ax.set_title(tiers[i])
        ax.set_xlabel('Signal onset - Question onset (ms)')
        ax.set_xlim(-5000, 5000)
        
    n_questions = len(plotting_df['question_start'].unique())
    plt.suptitle(f'Onset of Facial Signals Relative to Question Onset for {sa} Questions')    
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{sa}_relative_onset.png'))
    plt.close()


def plot_facial_signal_frequency(plotting_df, sa, out_dir, relative = False):
    
    counter = Counter(plotting_df['overlap_label'])
    tier_order = dict(zip(plotting_df['overlap_label'], plotting_df['tier']))
    
    if relative:
        counter = {i: counter[i] / len(plotting_df['overlap_label']) * 100.0 for i in counter}
        out_file = os.path.join(out_dir, f'{sa}_facial_signal_relative_frequency.png')  
    else:
        out_file = os.path.join(out_dir, f'{sa}_facial_signal_absolute_frequency.png')
    
    counter = {k: counter[k] for k in counter if type(k) is str} #exclude nan values
    df = pd.DataFrame({'FS': counter.keys(), 'Count': counter.values(), 'Tier': tier_order.values()}, 
                      index = np.arange(0, len(counter.keys()), 1))
    
    fig, ax = plt.subplots(figsize=(7,7))
    
    ax = sns.barplot(data = df, x = 'FS', y = 'Count', hue='Tier', dodge=False)

    if relative:
        for container in ax.containers:
            ax.bar_label(container, labels=[f'{x:,.2f}' for x in counter.values()])     
        ax.set_ylabel('Frequency (%)')
        ax.set_ylim(0, 100)
    else:
        for container in ax.containers:
            ax.bar_label(container)
        ax.set_ylabel('Count')
    
    ax.tick_params(axis='x', labelrotation=90)
    n_questions = len(plotting_df['question_start'].unique())
    ax.set_title(f'Absolute Frequencies of Facial Signal Overlaps for {sa} questions')
    
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()


def plot_percentual_overlap(plotting_df, sa, out_dir):
    fig, ax = plt.subplots(figsize=(16,7))
    plt.rcParams['text.usetex'] = True

    f = plotting_df.astype({'overlap_prct': float, 'overlap_label': str, 'tier': str})
    f = f[f['overlap_prct'] != 0.0]

    sns.boxplot(data=f, x="overlap_label", y="overlap_prct", hue="tier", dodge =False, width=.8,
                boxprops={"alpha": (.6)}, medianprops={"color": "coral"}, ax = ax)
    sns.stripplot(data=f, x="overlap_label", y="overlap_prct", hue="tier", linewidth=0.3, ax = ax)

    handles, labels = plt.gca().get_legend_handles_labels()
    ax.legend(handles[:8], labels[:8], loc='center right', bbox_to_anchor=(1.13, 0.5))
    ax.tick_params(axis='x', labelrotation=65)
    ax.set_xlabel('Facial Actions', fontsize = 13)
    ax.set_ylabel(r'Overlap in % ($\frac{dur\_overlap}{dur\_question} * 100$)', fontsize = 13)
    n_questions = len(plotting_df['question_start'].unique())
    ax.set_title(f'Proportional Overlap Of {sa} Questions And Facial Signals', fontsize = 15)
    ax.tick_params(axis='both', which='major', labelsize=12)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{sa}_Overlap_amounts.png'))
    plt.close()

