import pytest
from app import models


location_test_cases = [
    {
        'id': 'valid-coordinates',
        'coordinates': "POINT(-172.60453 -22.036201)",
        'latitude': -22.036201,
        'longitude': -172.60453,
        'str_val': "<Location (-22.036201, -172.60453)>"
    }, {
        'id': 'no-coordinates',
        'coordinates': None,
        'latitude': None,
        'longitude': None,
        'str_val': "<Location (None, None)>"
    }
]

location_test_cases_ids = \
    [case['id'] for case in location_test_cases]


@pytest.mark.parametrize('test_case', location_test_cases, ids=location_test_cases_ids)
def test_location(test_db, test_case):
    """
    Have to use test_db here because the PostGIS.Geometry base coordinates property does not change from
    a text based representation to an actual PostGIS.Geometry until it is saved to a database.
    """
    location = models.Location(coordinates=test_case['coordinates'])
    test_db.session.add(location)
    test_db.session.commit()
    assert location.latitude == test_case['latitude']
    assert location.longitude == test_case['longitude']
    assert str(location) == test_case['str_val']
