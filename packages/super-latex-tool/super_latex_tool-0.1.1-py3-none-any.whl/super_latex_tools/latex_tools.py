def generate_latex_table(data):
    if not data or not all(isinstance(row, list) for row in data):
        raise ValueError("Input data must be a non-empty list of lists.")
    
    if not all(len(row) == len(data[0]) for row in data):
        raise ValueError("All rows must have the same length.")
    
    num_columns = len(data[0])
    column_spec = "|".join(["c"] * num_columns)
    
    def iterate_rows(rows):
        if not rows:
            return ""
        head, *tail = rows  # get firts row to format
        formatted_head = " & ".join(map(str, head)) + " \\\\\n\\hline"
        return formatted_head + "\n" + iterate_rows(tail) # format other rows
    
    rows = iterate_rows(data)
    
    latex_code = (
        f"\\begin{{tabular}}{{|{column_spec}|}}\n"
        "\\hline\n"
        f"{rows}"
        "\\end{tabular}\n"
    )
    
    return latex_code
def generate_latex_image(image_path, caption="An image"):
    latex_code = f"""
    \\begin{{figure}}[h]
        \\centering
        \\includegraphics[width=0.5\\textwidth]{{{image_path}}}
        \\caption{{{caption}}}
    \\end{{figure}}
"""
    return latex_code.strip()
