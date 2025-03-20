import subprocess
import os
from pathlib import Path
from mygenlatex.bin.generators import generate_table, generate_document, generate_image

def generate_pdf():
    planet_data = [
        ["Planet", "Mass (mnogo kg)", "Diameter (km)", "Moons", "Type"],
        ["Mercury", 0.330, 4879, 0, "Terrestrial"],
        ["Venus", 4.87, 12104, 0, "Terrestrial"],
        ["Earth", 5.97, 12756, 1, "Terrestrial"],
        ["Mars", 0.642, 6792, 2, "Terrestrial"],
        ["Jupiter", 1898.0, 139820, 79, "Gas Giant"],
        ["Saturn", 568.0, 116460, 82, "Gas Giant"]
    ]

    latex_table = generate_table(planet_data)
    latex_image = generate_image("../images/gofman.jpeg", "Igor Gofman")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    tex_filename = output_dir / "doc.tex"
    pdf_filename = output_dir / "doc.pdf"

    generate_document(tex_filename, latex_table + latex_image)
    
    try:
        subprocess.run(
            ["pdflatex", "-output-directory", str(output_dir), "-interaction=nonstopmode", str(tex_filename)],
            check=True,
            stdout=subprocess.DEVNULL
        )
        print(f"PDF успешно сгенерирован: {pdf_filename}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка компиляции PDF: {e}")

if __name__ == "__main__":
    generate_pdf()