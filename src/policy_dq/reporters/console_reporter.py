def print_summary(errors):

    if not errors:

        print("All validations passed")

        return

    print(f"{len(errors)} validation errors found")

    for e in errors:

        print(
            f"{e.rule_name} | {e.field} | {e.message} | row {e.row}"
        )