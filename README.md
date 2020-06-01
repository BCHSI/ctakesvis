## a CTAKES concept visualization tool

This tool overlays concepts / tokens extracted by UCSF CTAKES client with an original text.

To generate a visualization, run:

    python ctakesvis.py [-html] [plain text: path/to/note.txt] [ctakes extract: path/to/note_combined_output.json]

    python ctakesvis.py [plain text note] [directory of ctakes extract]

# Demo

![](demo-small.gif)

# Generating summaries

the tool will output an Index page, which can come with summaries (e.g. counts of concepts per domain) if respective
parameters are included

    ./ctakesvis.py samples/ samples-extracts/samples -a count -b domain -f cui
    # -a : aggregate using count function
    # -b : by column 'domain'
    # -f : aggregate field 'cui' (any field works in this example for 'count' function)


