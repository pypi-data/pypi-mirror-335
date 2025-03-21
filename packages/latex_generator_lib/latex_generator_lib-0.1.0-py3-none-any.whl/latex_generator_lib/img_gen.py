def format_latex_image(path: str, dimensions: tuple, measurement_unit: str = "px") -> str:
    """Создает LaTeX код для включения изображения с заданными размерами."""
    width, height = dimensions
    figure_template = (
        "\\begin{figure}[h]\n"
        "\\centering\n"
        "\\includegraphics[width={width}{unit}, height={height}{unit}]{{{path}}}\n"
        "\\end{figure}"
    )
    
    return figure_template.format(width=width, height=height, unit=measurement_unit, path=path)
