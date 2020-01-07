#!/usr/bin/env python
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import pandas as pd
import json
import re

def annotation_json2html(txt, anns,
                   start = 'start',
                   end = 'end',
                   label='label',
                   location='location',):
    if isinstance(anns, (list, tuple)):
        anns = sorted(anns, key = lambda x: x[start])
    prev_end = 0
    html_ = ''
    for ii, ann in enumerate(anns):
        label_ = ann[label]
        if ann['negated']:
            label_ = '&#10060; ' + label_
        tip_text = f'<i>{ii}:</i> {label_}'
        if (location in ann) and (ann[location]):
            location_ = ann[location]
            tip_text += f'<br/><i>in: </i> ' + location_
        tip_text = f'<a href="#row_{ii}" class="ttt" >{tip_text}</a>'

        if 'domain' in ann:
            domain = ann['domain'].replace(' ', '_')

        if (ann[start]-prev_end)>0:
            html_+= ('<span>' + txt[prev_end:ann[start]].replace('\n','<br/>\n') + '</span>')

        if (ann[end]-prev_end)>0:
            prefix = ''
            word = txt[ann[start]:ann[end]]
        else:
            prefix = ' '
            word = '&dagger;'
        #onclick="deleteConcept(this)"
        html_+= (prefix 
                 + f'<div class="ttooltip" id="entity_{ii}"><span class={domain}>{word}'
                 + f'</span><span class="tooltiptext" id="tooltiptext_{ii}">{tip_text}</span></div>')
        prev_end = ann[end]
    return html_


def concat_concepts(results, start='offset_start'):
    """flattens the `.domains` field and adds `concepts.name` field to the list"""
    concepts = []
    for res in results['domains']:
        domain = res['name'].replace(' ', '_')
        concepts_ = res['concepts']
        for entry in concepts_:
            entry['domain'] = domain
            for col in ['conditional', 'hof', 'negated']:
                if col not in entry:
                    continue
                entry[col] = (entry[col] == 't')
        concepts.extend(concepts_)

    concepts = sorted(concepts, key = lambda x: x[start])
    return concepts

def add_css_head(html_):

    out = ('''<head>
  <link rel="stylesheet" href="../styles.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
  <script src="../scripts.js" type="text/javascript"></script>
</head>''' +
f'''<body>
  {html_}
</body>''')
    return out

if __name__ == '__main__':
    import argparse
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument('report', help='report text file path', type=str)
    parser.add_argument('json', help='file path of the JSON-formatted CTAKES extract or folder that contains it', 
                        type=str)
    parser.add_argument('--report-dir', help='report text directory', type=str)
    parser.add_argument('--no-table', action="store_false", default=True,
                        dest='table')
    parser.add_argument('--no-save', action="store_true", default=False)
    parser.add_argument('--no-browser', action="store_false", default=True,
                        dest='browser')
    parser.add_argument('--html-dir', help='folder to store an html file', default='html')
    args = parser.parse_args()
    save = ~ args.no_save


    id = os.path.split(args.report)[-1].replace('.txt', '')
    if os.path.isdir(args.json):
        fn_json = os.path.join(args.json, id + '_combined_output.json')
    else:
        fn_json = args.json

    with open(args.report) as fh:
        txt = fh.read()

    with open(fn_json) as fh:
        results = json.load(fh)

    concepts = concat_concepts(results)
    html_ = annotation_json2html(txt, concepts, start='offset_start', end='offset_end',
                        label='canon_text')

    #html_ = '<br/>' + html_
    COL_ORDER=['canon_text',
               'negated',
               'location',
               'domain',
               'hof',
               'imputed_time',
               'value',
               'conditional',
               'cui',
               'location_snomed_id',
               'vocab_term',
               'vocab',
              #  'offset_end',
              #  'offset_start',
              #  'range_text',
              ]
    if args.table:
        pd.set_option('display.max_rows', len(concepts)+1)
        concepts_df = pd.DataFrame(concepts)
        concepts_df = concepts_df[COL_ORDER]
        concepts_df.loc[concepts_df['domain'] =='signs_and_symptoms', 'domain'] = 'symptoms'
        def modify_column_names(x):
            if x=='hof':
                return 'past'
            else:
                return x.replace('_', ' ')

        concepts_df.columns = concepts_df.columns.map(modify_column_names)
        
        #concepts_df.drop('note_id', axis=1, inplace=True)
        concepts_df_str = concepts_df.applymap(str)
        concepts_df_str[concepts_df.applymap(lambda x: (x=='na') or (x is None))] = ''
        concepts_df_str[concepts_df == False] = ''
        for col in ['negated','location','domain', 'past']:
            if col not in concepts_df_str:
                continue
            concepts_df_str[col] = concepts_df_str[col].str.lower()

        drop_cols = concepts_df_str.columns[(concepts_df_str == '').all(0)]
        concepts_df_str.drop(drop_cols, axis=1, inplace=True)
        concept_html = concepts_df_str._repr_html_()
        concept_html = re.sub(r'<tr>\n      <th>(\d+)</th>\n(\s+)<td>(.*)</td>',
                              r'<tr class="entity_row" id="row_\1">\n      '+
                              r'<th id="row_\1">\1</th>\n\2<td><a href="#entity_\1">\3</td>',
                             #r'<tr>\n      <th>(\d+)</th>\n',
                             # r'<tr class="entity_row" id="row_\1">\n      '+
                             # r'<th class="entity_id_cell" >\1</th>\n',
                              concept_html)
        concept_html = concept_html.replace('<tr style="text-align: right;">', '<tr>')
        # re.sub(r"\<th\>(\d+)\<th\>", r"\1,\2", coords)
        # concept_html.replace('<th> name="chapter')
        html_ = (f'<div class="left"><div class="left-sub">{html_}</div></div>\n' +
                 f'<div class="right">{concept_html}</div>')

    html_ = add_css_head(html_)

    if save:
        from pathlib import Path

        parent = os.getcwd()
        os.makedirs(os.path.join(parent, args.html_dir), exist_ok=True)

        path = os.path.join(parent, args.html_dir, f'{id}.html')
        path = Path(path)
        url = path.absolute().as_uri()

        print(f'saving to:\t{path}')
        with open(path, 'w') as fh:
            fh.write(html_)
        
        if args.browser:
            import webbrowser
            webbrowser.open(url)
    else:
        print(html_)
