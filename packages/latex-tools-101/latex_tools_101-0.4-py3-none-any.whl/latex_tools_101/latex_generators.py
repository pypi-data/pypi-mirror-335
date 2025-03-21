import subprocess

latex_dependencies = {
    'generate_table_tex': '\\usepackage[utf8]{inputenc}\n',
    'generate_image_tex': '\\usepackage{graphicx}\n'
}

def execute_functions(*func_args_tuples):
    code =  '\\begin{document}\n'
    overhead = '\\documentclass{article}\n'
    for func, args in func_args_tuples:
        if func.__name__ in latex_dependencies:
            overhead += latex_dependencies[func.__name__]
        code += func(*args)
    code += '\\end{document}\n'

    return overhead + code

def generate_table_tex(data):
    n = len(data[0])
    if not data:
        return ''
    
    code = (
        '\\begin{tabular}{|' + 'c|' * n + '}\n'
        '\\hline\n'
    )
    
    for line in data:
        code += ' & '.join(line) + ' \\\\\n'
        code += "\\hline\n"
    
    code += '\\end{tabular}\n'
    
    return code

def generate_image_tex(img_path):
    code = (
        '\\begin{center}\n'
        f'\t\\includegraphics[width=1\\textwidth]{{{img_path}}}\n'
        '\\end{center}\n'
    )

    return code

def execute_tex(file_path):
    subprocess.run(['pdflatex', file_path], check=True)
