def table_generator(table):
    answer = ""
    
    sz = 0
    for row in table:
        sz = max(sz, len(row))
    res = "\\begin{tabular}{" + " " + "|c" * sz + "|" + " " + "}\n"
    answer += res
    
    answer += "\\hline\n"

    for row in table:
        answer += " & ".join(row)
        answer += " \\\\\n"
    answer += "\\end{tabular}"

    return answer

def image_generator(path, row, width=None, height=None):
    answer = ""
    
    answer += "\\begin{figure}[h]\n"
    
    answer += "\\centering\n"

    answer += "\\includegraphics["
    if height:
        answer += ("height=" + str(height))
        if width:
            answer += (",width=" + str(width))
    elif width:
        answer += ("width=" + str(width))
    answer += ("\\linewidth]{" + path + "}\n")

    answer += ("\\caption{" + row + "}\n")

    answer += "\\label{fig:mpr}\n"

    answer += "\\end{figure}"
    
    return answer
        
