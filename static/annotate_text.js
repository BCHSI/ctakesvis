function replaceNewline(txt){
    return txt.replace(/(?:\r\n|\r|\n)/g, '<br>\n')
}


function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        return ((x < y) ? -1 : ((x > y) ? 1 : 0));
    });
}

function annotateTextWithJson(txt, anns,
                              start = "start",
                              end = "end",
                              label = "label",
                              loc = "location",
                              highlight = "domain",
                              negation_symbol="&#10060;") {
    var domain, prefix,
    chunk_start, chunk_end, 
    tip_text, txt_span, word;

    var prev_end = 0;
    var prev_start = 0;
    var html = "";
    var ann;

    console.log("highlighting: "+ highlight);
    anns = sortByKey(anns, start);
    console.log("annotations length " + anns.length);
    for (var ii = 0; (ii < anns.length); ii += 1) {
        var domain = "";
        ann = anns[ii];
        // console.log("annotation " + ii);
        // console.log(ann);
        chunk_label = ann[label];
        if (("negated" in ann) && ann["negated"]) {
            chunk_label = (negation_symbol + " " + chunk_label);
        }
        tip_text = `<i>${ii}:</i> ${chunk_label}`;
        if ((loc in ann) && ann[loc]) {
            loc = ann[loc];
            tip_text += (`<br/><i>in: </i> ` + loc);
        }
        tip_text = `<a href="#row_${ii}" class="ttt" >${tip_text}</a>`;
        if (highlight in ann) {
            domain = ann[highlight]; //.replace(" ", "_");
        }
        try {
            chunk_start = Number.parseInt(ann[start]);
            chunk_end = Number.parseInt(ann[end]);
        } catch(ee) {
            if ((ee instanceof ValueError)) {
                console.warn(ee.toString());
                continue;
            } else {
                throw ee;
            }
        }
        if (chunk_start > prev_end) {
            //try {
                txt_span = replaceNewline(txt.slice(prev_end, chunk_start));
                html += "<span>" + txt_span + "</span>";
                prefix = "";
                word = txt.slice(chunk_start, chunk_end);
            /*
            } catch(ee) {
                if ((ee instanceof TypeError)) {
                    throw ee;
                } else {
                    throw ee;
                }
            }
            */
        } else {
            if ((chunk_end > prev_end)) {
                prefix = " ";
                word = txt.slice(prev_end, chunk_end);
            } else {
                prefix = "";
                word = "<sup>&dagger;</sup>";
            }
        }

        var new_chunk = (prefix +
                        `<div class="ttooltip" id="entity_${ii}">` +
                        `<span class="${domain}">${word}</span>` + 
                        `<span class="tooltiptext" id="tooltiptext_${ii}">` +
                        `${tip_text}</span></div>`);
        html += new_chunk
        prev_start = chunk_start;
        prev_end = Math.max(chunk_end, prev_end);
    }
    txt_span = replaceNewline(txt.slice(prev_end));
    html += ("<span>" + txt_span + "</span>");
    return html;
}
