import json


def generate_json_report(errors, output_path):

    result = [
        {
            "rule_name": e.rule_name,
            "field": e.field,
            "message": e.message,
            "row": e.row,
        }
        for e in errors
    ]

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)