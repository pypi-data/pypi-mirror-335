from hw_2 import generate_table, generate_image, gererate_latex_and_pdf


def main():
    sample_data1 = [
        ["Name", "Age", "City"],
        ["Mary", "23", "Moscow"],
        ["Tatyana", "42", "Nizhny Novgorod"],
        ["Alexander", "31", "Novosibirsk"],
        ["Paul", "37", "Yakutsk"],
    ]

    latex1 = generate_table(sample_data1)
    gererate_latex_and_pdf(latex1, "sample_data1.tex")

    image_path = "PNG_transparency_demonstration_1.png"

    latex2 = generate_image(image_path)
    gererate_latex_and_pdf(latex2, "sample_data2.tex")


if __name__ == "__main__":
    main()
