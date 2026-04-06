from policy_dq.validators.cross_field import validate_cross_field


def test_cross_field():

    data = [
        {
            "start_date": 10,
            "end_date": 5
        }
    ]

    rule = {

        "name": "date_rule",

        "type": "cross_field",

        "fields": [
            "start_date",
            "end_date"
        ],

        "condition": "end_date >= start_date"
    }

    errors = validate_cross_field(data, rule)

    assert len(errors) == 1