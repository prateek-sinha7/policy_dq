def generate_markdown_report(errors, output_path):

    lines = [
        "# Validation Report",
        "",
        "| Rule | Field | Message | Row |",
        "|------|-------|---------|-----|",
    ]

    for e in errors:

        lines.append(
            f"| {e.rule_name} | {e.field} | {e.message} | {e.row} |"
        )

    with open(output_path, "w") as f:

        f.write("\n".join(lines))