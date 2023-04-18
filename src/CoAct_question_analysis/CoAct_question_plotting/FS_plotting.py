import os
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from d3blocks import D3Blocks

#TODO relative numbers

def plot_cooccurrence_matrix(matrix, sa, out_dir):
    
    #melt upper triangle of matrix
    lower_matrix = matrix.where(np.tril(np.ones(matrix.shape)).astype(np.bool))
    
    plt.figure(figsize=(12, 10))
    ax = sns.heatmap(lower_matrix, cmap="crest", annot=True, fmt=".0f")
    for t in ax.texts:
        if float(t.get_text())> 0:
            t.set_text(t.get_text()) #if the value is greater than 0 then I set the text 
        else:
            t.set_text("") # if not it sets an empty text
            
    ax.set_title(f'Co-occurrence of Facial Signals in {sa} questions')
    plt.tight_layout()
    ax.get_figure().savefig(os.path.join(out_dir, f'{sa}_FS_matrix.png'))
    plt.close()

def plot_chord_diagram(matrix, sa, out_dir):
    
    d3 = D3Blocks(chart='Chord', frame=False)

    #melt upper triangle of matrix
    df = matrix.where(np.triu(np.ones(matrix.shape)).astype(np.bool))
    df = df.stack().reset_index()
    df.columns = ['source','target','weight']

    #exclude self references
    df = df[df['source'] != df['target']]

    filepath = os.path.join(out_dir, f'{sa}_facial_actions_chord_plot.html')
    d3.chord(df, fontsize = 14, cmap = 'tab20', showfig = False, filepath=filepath)
