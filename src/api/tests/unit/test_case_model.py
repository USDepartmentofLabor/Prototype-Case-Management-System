import re
from app import models


def test_case_key_generation(test_client, test_db):
    user = models.User.query.filter_by(username='admin').first()

    cd = models.CaseDefinition(key='TCD', name="Test Case Definition", created_by=user, updated_by=user)
    test_db.session.add(cd)
    test_db.session.commit()

    c = models.Case(name='Test Case', case_definition_id=cd.id, created_by=user, updated_by=user)

    assert c.key
    my_reg_ex = r"^" + re.escape(cd.key) + r"-\d+"
    assert re.search(my_reg_ex, c.key)


def test_case_key_generation_with_no_cases(test_client, test_db):
    user = models.User.query.filter_by(username='admin').first()

    cd = models.CaseDefinition(key='TCD', name="Test Case Definition", created_by=user, updated_by=user)
    test_db.session.add(cd)
    test_db.session.commit()

    case_key = models.Case.generate_key(cd.id)
    my_reg_ex = r"^" + re.escape(cd.key) + r"-1"
    assert re.search(my_reg_ex, case_key)


def test_case_key_generation_with_cases(test_client, test_db):
    user = models.User.query.filter_by(username='admin').first()

    cd = models.CaseDefinition(key='TCD', name="Test Case Definition", created_by=user, updated_by=user)
    test_db.session.add(cd)
    test_db.session.commit()

    c = models.Case(name='Test Case', case_definition_id=cd.id, created_by=user, updated_by=user)
    test_db.session.add(c)
    test_db.session.commit()

    case_key = models.Case.generate_key(cd.id)
    my_reg_ex = r"^" + re.escape(cd.key) + r"-" + str(c.id + 1)
    assert re.search(my_reg_ex, case_key)


def test_default_status_used_when_not_provided(test_client, test_db):
    default_status = models.CaseStatus.query.filter_by(default=True).first()
    user = models.User.query.filter_by(username='admin').first()

    cd = models.CaseDefinition(key='TCD', name="Test Case Definition", created_by=user, updated_by=user)
    test_db.session.add(cd)
    test_db.session.commit()

    case = models.Case(name='Test Case', case_definition_id=cd.id, created_by=user, updated_by=user)

    assert case.status
    assert case.status_id == default_status.id
