def latex_figure(image_path: str, caption: str = "", label: str = "", width: str = "0.8\\linewidth") -> str:
    return f"""
\\begin{{figure}}[h]
    \\centering
    \\includegraphics[width={width}]{{{image_path}}}
    \\caption{{{caption}}}
    \\label{{{label}}}
\\end{{figure}}
"""