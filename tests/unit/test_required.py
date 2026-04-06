from policy_dq.validators.required import validate_required


def test_required():

    data = [{"email": ""}]

    rule = {
        "name": "email_required",
        "type": "required",
        "field": "email"
    }

    errors = validate_required(data, rule)

    assert len(errors) == 1