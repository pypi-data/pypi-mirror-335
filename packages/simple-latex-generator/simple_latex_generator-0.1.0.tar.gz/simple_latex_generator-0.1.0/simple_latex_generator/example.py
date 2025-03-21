import simple_latex_generator as slg


if __name__ == "__main__":
    table = [
        ["Header 1", "Header 2"],
        ["Data 1", "Data 2"],
        ["Special & chars", "100%"]
    ]

    latex_code = slg.generate_latex_table(table) + '\n\n\n'
    latex_code += slg.generate_latex_image('meme.png')
    slg.save_tex(latex_code, 'test.tex')