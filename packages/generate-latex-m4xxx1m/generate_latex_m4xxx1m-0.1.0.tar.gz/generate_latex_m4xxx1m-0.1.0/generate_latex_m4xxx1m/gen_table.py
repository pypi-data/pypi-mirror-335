from typing import List, Any

def generate_table(table: List[List[Any]]) -> str:
    assert len(table) > 0
    width = len(table[0])
    assert width > 0 and all(len(row) == width for row in table)

    header = f'''\\begin{{center}}
\\begin{{tabular}}{{|{'c|' * width}}}
\\hline\n'''
    body = ' \\\\\n\\hline\n'.join(map(lambda row: ' & '.join(map(str, row)), table))
    footer = ''' \\\\
\\hline
\\end{tabular}
\\end{center}\n'''

    return header + body + footer
