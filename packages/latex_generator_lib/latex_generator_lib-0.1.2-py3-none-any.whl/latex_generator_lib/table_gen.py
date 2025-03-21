def latex_table(data: list[list]) -> str:
    """Создает LaTeX код для отображения таблицы с предоставленными данными."""
    
    if not data or not data[0]:
        return ""
    
    column_specification = create_column_spec(len(data[0]))
    
    table_content = []
    table_content.append(format_table_header(column_specification))
    
    table_rows = format_table_rows(data)
    table_content.extend(table_rows)
    
    table_content.extend([
        "\\end{tabular}",
        "\\end{table}"
    ])
    
    return "\n".join(table_content)

def create_column_spec(column_count: int) -> str:
    """Создает спецификатор колонок для табличной среды LaTeX."""
    return f"|{'|'.join(['c' for _ in range(column_count)])}|"

def format_table_header(column_spec: str) -> str:
    """Формирует заголовок и начало LaTeX таблицы."""
    return f"\\begin{{table}}[h]\n\\centering\n\\begin{{tabular}}{{{column_spec}}}\n\\hline"

def format_table_rows(data: list[list]) -> list[str]:
    """Форматирует строки таблицы, заменяя специальные символы."""
    rows = []
    for row in data:
        formatted_cells = [str(cell).replace("_", "\\_") for cell in row]
        rows.append(" & ".join(formatted_cells) + " \\\\")
        rows.append("\\hline")
    return rows
