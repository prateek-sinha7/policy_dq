from policy_dq.models import ValidationError
from policy_dq.reporters.json_reporter import generate_json_report


def test_json_report(tmp_path):

    errors = [
        ValidationError(
            rule_name="test",
            field="age",
            message="invalid",
            row=0,
        )
    ]

    file = tmp_path / "report.json"

    generate_json_report(
        errors,
        file,
    )

    assert file.exists()