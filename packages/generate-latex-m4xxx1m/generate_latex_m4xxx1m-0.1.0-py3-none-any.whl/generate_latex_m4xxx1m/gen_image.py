def generate_image(path_to_image: str, width: str = '\\textwidth'):
    return f'''\\begin{{center}}
\\includegraphics[width={width}]{{{path_to_image}}}
\\end{{center}}
'''
