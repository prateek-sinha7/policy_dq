from policy_dq.validators.type_check import validate_type


def test_type_validation():

    data = [{"age": "abc"}]

    rule = {
        "name": "age_type",
        "type": "type",
        "field": "age",
        "dtype": "int",
    }

    errors = validate_type(data, rule)

    assert len(errors) == 1