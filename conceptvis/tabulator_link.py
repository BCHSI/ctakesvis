import json
import pandas as pd

HEADER = """
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="{static}/styles.css">
  {colorscheme}
  <link href="{static}/tabulator/dist/css/tabulator.min.css" rel="stylesheet">
  
  <script type="text/javascript" src="{static}/jquery.min.js"></script>
  <script type="text/javascript" src="{static}/scripts.js" ></script>

  <script type="text/javascript" src="{static}/tabulator/dist/js/tabulator.min.js"></script>
  <script type="text/javascript" src="{static}/annotate_text.js"></script>
  <script type="text/javascript" src="{static}/table_schema.js"></script>
</head>
"""

boilerplate_data = """
  <script type="text/javascript">

    var tabledata = {tabledata};
    var txt = `{text}`;
    var highlight = {highlight};

    var html1 = annotateTextWithJson(txt, tabledata,
                                     start ="{start}",        // "offset_start"
                                     end = "{end}",            // "offset_end"
                                     label="{label}",          // "canon_text"
                                     loc = "{location}",       // "location"
                                     highlight=highlight);   // "domain"
    $(".left-sub").append(html1);

    var schema = {schema};
    var name_mapping = {name_mapping};

    var tbl = createTable("{tag}", tabledata, schema,
               highlight=highlight, name_mapping=name_mapping,
               layout={layout}, vertical={vertical},
               height={height}, firstColWidth={first_col_width},
               href={href});
  </script>
"""

boilerplate_index = \
"""
  <script type="text/javascript">

    var tabledata = {tabledata};
    var highlight = {highlight};
    var schema = {schema};
    var name_mapping = {name_mapping};

    var tbl = createTable("{tag}", tabledata, schema,
               highlight=highlight, name_mapping=name_mapping,
               layout={layout}, vertical={vertical},
               height={height}, firstColWidth={first_col_width},
               href={href});
  </script>
"""


def _col_types_for_js(typestring):
    if typestring == 'bool':
        return "boolean"
    elif ("float" in typestring) | ("int" in typestring):
        return "number"
    elif ("date" in typestring):
        return "date"
    else:
        return "string"


def get_col_types_for_js(concept_dict_list):
   return (pd.DataFrame(concept_dict_list[:10])
    .dtypes.astype(str).map(_col_types_for_js)
    .to_dict()
    )


def get_head(colors=None, static='./static'):
    if colors is not None:
        colorscheme = f'<link rel="stylesheet" href="{static}/{colors}">'
    else:
        colorscheme=""
    head = HEADER.format(colorscheme=colorscheme, static=static)
    return head


def get_schema(concepts, col_order, **kwargs):
    # {title:"Name", field:"name", sorter:"string", width:150, hozAlign:"left", formatter:"progress", sortable:false},
    col_types = get_col_types_for_js(concepts)
    col_list = []
    if col_order is None or len(col_order)==0:
        col_order = col_types.keys()

    for cc in col_order:
        col_list.append({
            "title":  cc.replace('_', ' '),
            "field":  cc,
            "sorter": col_types[cc]
            })
    return col_list


def vis_report(text, concepts, 
                 col_order = [], name_mapping = {}, 
                 start="start",
                 end="end",
                 label="label",
                 location='location',
                 tag = 'concept-table', 
                 highlight=None, 
                 vertical=True,
                 layout="fitColumns", 
                 height='96.5%',
                 href='id',
                 first_col_width="20%",
                 colorscheme = None,
                 static='./static',
                 **kwargs):
    "generate javascript table data and code"
    head = get_head(colorscheme, static=static)
    schema = get_schema(concepts=concepts, col_order=col_order)
    schema = json.dumps(schema).replace('}, ', '},\n    ')

    concept_table_html = f'''<div id="{tag}"></div>
      <div class="table-controls">
      <button id="download-csv">Download CSV</button>
      <button id="download-json">Download JSON</button>
      <!--
      <button id="download-xlsx">Download XLSX</button>
      <button id="download-pdf">Download PDF</button>
      --!>
      </div>
    '''

    main_dish = boilerplate_data.format(
                        text = text,
                        tabledata=json.dumps(concepts),
                        start = start,
                        end = end,
                        label = label,
                        location = location,
                        tag = tag,
                        highlight = json.dumps(highlight),
                        schema = schema,
                        name_mapping = json.dumps(name_mapping),
                        vertical=json.dumps(vertical),
                        layout=json.dumps(layout),
                        height=json.dumps(height),
                        href = json.dumps(href),
                        first_col_width = json.dumps(first_col_width),
                        )
    html = (head + '<div class="left"><div class="left-sub">' +
             '</div></div>\n' +
             '<div class="right">' + concept_table_html +'</div>' + main_dish)
    return html



def get_table_js(concepts, col_order = [], name_mapping = {}, 
                 tag = 'concept-table', highlight=None, 
                 vertical=True, layout="fitColumns", 
                 height='100%', href='id',
                 first_col_width="20%",
                 static='./static', 
                 **kwargs):
    "generate javascript table data and code"
    head = get_head(static=static)
    schema = get_schema(concepts=concepts, col_order=col_order)
    schema = json.dumps(schema).replace('}, ', '},\n    ')
    return head + boilerplate_index.format(
                        tag = tag,
                        highlight = json.dumps(highlight),
                        schema = schema,
                        name_mapping = json.dumps(name_mapping),
                        tabledata=json.dumps(concepts),
                        vertical=json.dumps(vertical),
                        layout=json.dumps(layout),
                        height=json.dumps(height),
                        href = json.dumps(href),
                        first_col_width = json.dumps(first_col_width),
                        )
