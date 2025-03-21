def build_table(dataset):
    column_count = len(dataset[0]) if dataset else 0
    alignments = "|".join(["c"] * column_count)
    tabular_header = "\\begin{tabular}{|" + alignments + "|}\n\\hline\n"
    tabular_footer = "\\end{tabular}"

    processed_rows = []
    for entry in dataset:
        row_content = " & ".join(map(str, entry)) + " \\\\ \\hline"
        processed_rows.append(row_content)

    table_data = "\n".join(processed_rows)
    latex_code = tabular_header + table_data + "\n" + tabular_footer
    return latex_code


def insert_picture(graphic_path, description="", marker=""):
    figure_template = r"""
\begin{figure}[h]
    \centering
    \includegraphics[width=0.8\linewidth]{%s}
    \caption{%s}
    \label{%s}
\end{figure}
    """ % (graphic_path, description, marker)
    return figure_template
