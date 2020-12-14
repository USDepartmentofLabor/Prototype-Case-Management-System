from unittest.mock import MagicMock, patch
import pytest
from flask import g
from app.cases.cases_service import CasesService


def test_can_init():
    session = MagicMock()
    service = CasesService(json_args={'foo': 'bar'}, _session=session)
    assert service.session is session
    assert service.json_args['foo'] == 'bar'

