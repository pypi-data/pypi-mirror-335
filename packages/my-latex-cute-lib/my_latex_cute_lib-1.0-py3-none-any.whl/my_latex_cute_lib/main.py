import os

def table_to_latex(table_array, file_path='table.teh'):
    """
    https://www.overleaf.com/learn/latex/Tables
    :param table_array: array like [[col_1, col_2], [1, 2], [3, 4]]
    :param file_path: name of the file (default='table.teh')
    :return: .tex file like
    _____________
    col_1 | col_2
    _____________
    1 | 2
    3 | 4
    _____________
    """
    with open(file_path, 'w', encoding='ansi') as f:
        latex = r"""\documentclass{article}
\usepackage{booktabs}
\begin{document}
\begin{table}[h]
\begin{tabular}"""
        latex += '{|' + '|'.join(['c'] * len(table_array[0])) + '|}' + '\n\\toprule\n'

        latex += ' & '.join([f'\\textbf{{{col}}}' for col in table_array[0]]) + r' \\' + '\n\\midrule'

        for row in table_array[1:]:
            latex += '\n' + ' & '.join(map(str, row)) + r' \\'

        latex += r"""
\bottomrule
\end{tabular}
\end{table}
\end{document}
"""
        f.write(latex)


def img_to_latex(img_path='malone.png', file_path='img.teh'):
    """
    https://www.overleaf.com/learn/latex/Inserting_Images
    :param img_path: path to image
    :param file_path: path to .teh file (if the file is created, the image will be added to it)
    :return: .teh file with img
    """
    img_path = os.path.abspath(img_path).replace('\\', '/')
    path_to_folder = img_path[:img_path.rfind('/')]
    file_name = img_path[img_path.rfind('/') + 1:img_path.rfind('.')]
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='ansi') as f:
            latex = r"""\documentclass{article}
\usepackage{graphicx}
\graphicspath{ {""" + path_to_folder + r"""} }
\usepackage[rightcaption]{sidecap}
\usepackage{wrapfig}
\includegraphics[scale=0.5]{""" + file_name + r"""}
\end{document}"""
            f.write(latex)
    else:
        libs_line = r"""\usepackage{graphicx}
\graphicspath{ {""" + path_to_folder + r"""} }
\usepackage{wrapfig}
\usepackage[rightcaption]{sidecap}"""
        file_line = r"""\includegraphics[scale=0.5]{ """ + file_name + """}}"""
        with open(file_path, 'r', encoding='ansi') as f:
            lines = f.readlines()

            for i, line in enumerate(lines):
                if '\\documentclass{article}' in line:
                    lines.insert(i + 1, libs_line + '\n')
                elif '\\end{document}' in line:
                    lines.insert(i, file_line + '\n')
                    break

            with open(file_path, 'w', encoding='ansi') as f:
                f.writelines(lines)