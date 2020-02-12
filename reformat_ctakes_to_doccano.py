#!/usr/bin/env python
# coding: utf-8
import json
import os
import pandas as pd
from ctakesvis import concat_concepts


def convert_row_to_doccano_input(x):
    """Output format:
    [[start, end, label],
     [start, end, label],
     ...]
    """
    return [x['offset_start'], x['offset_end'], x['label']]


def construct_label(x):
    """This is a toy example function for selecting (narrowing down)
    a set of labels based on CTAKES annotation.
    In this case we simply take a term domain, 
    such as 'disease', 'symptoms', 'meds', or 'procedures'
    and whether they are marked as 'negated' or 'history' ('hof').
    
    depending on your particular application, 
    you might want to narrow down your labels
    based on a specific set of terms 
    (e.g. only certain class of medications, 
    or symptoms of a particular disease)
    """
    if x['negated']:
        return 'neg_' + x['domain']
    elif x['hof']:
        return 'hx_' + x['domain']
    else:
        return x['domain']


import argparse
parser = argparse.ArgumentParser(
description='Convert notes with annotations to a JSONL file compatible with Doccano labelling tool'
                             )

parser.add_argument('reports', help='report text file path', type=str)
parser.add_argument('jsons', help='file path of the JSON-formatted CTAKES extract or folder that contains it',
                    type=str)
parser.add_argument('-o', '--output', help='output file', type=str)
args = parser.parse_args()


if args.output is None:
    outdir = '.'
    #os.makedirs(outdir, exist_ok=True)
    out_filepath = os.path.join(outdir, f'{args.reports}-ctakes.jsonl')
else:
    out_filepath = args.output

lines = ''
    
for file in os.scandir(args.reports):
    ctakes_filename = file.name.replace('.txt','_combined_output.json')
    ctakes_filepath = os.path.join(args.jsons, ctakes_filename)
    
    txt_filepath = file.path
    
    if not os.path.exists(ctakes_filepath):
        continue
        
    print(file.name)

    # read a text file 
    with open(txt_filepath) as fh:
        txt = fh.read()
    print('# characters:',  len(txt))

    # read CTAKES JSON
    with open(ctakes_filepath) as fh:
        concepts = json.load(fh)
    # format CTAKES JSON
    concepts = concat_concepts(concepts)
    concepts = pd.DataFrame(concepts)
    print('# concepts:' , len(concepts))
    print()
    if len(concepts) == 0:
        continue

    # if there are more than one label per concept,
    # take first one (yes, this is arbitrary)
    concepts_unique = concepts[['hof','negated', 'domain', 'offset_start', 'offset_end',
              ]].groupby(['offset_start', 'offset_end',]).first().reset_index()
    # simplify domain names
    concepts_unique['domain'] = concepts_unique['domain'].map(lambda x: x.split('_')[-1])
    concepts_unique['label'] = concepts_unique.apply(construct_label, 1)
    
    # convert a dataframe to a list of lists: 
    # [[start, end, label],       [start, end, label],       ...]
    label_list = (concepts_unique
         .apply(convert_row_to_doccano_input, 1)
         .tolist())
    
    lines += json.dumps(
        {'text': txt,
        'labels':label_list
        }) + '\n'

lines = lines.rstrip('\n')

print('SEE:', out_filepath)
with open(out_filepath, 'w') as fh:
    fh.write(lines)


