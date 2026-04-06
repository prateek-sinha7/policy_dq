from policy_dq.validators.uniqueness import validate_unique


def test_unique():

    data = [
        {"id": 1},
        {"id": 1},
    ]

    rule = {
        "name": "unique_id",
        "type": "unique",
        "field": "id",
    }

    errors = validate_unique(data, rule)

    assert len(errors) == 1