def generate_latex(body: list[str]):
    header = r'''\documentclass{article}

\usepackage[english,russian]{babel}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}

\begin{document}
'''
    footer = '\\end{document}\n'
    return '\n'.join([header] + body + [footer])
