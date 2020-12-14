from app.models import SurveyResponse, SurveyResponseStatus


def test_default_status_used_when_not_provided(test_client, test_db):
    default_status = SurveyResponseStatus.query.filter_by(default=True).first()
    survey_response = SurveyResponse()
    assert survey_response.status
    assert survey_response.status_id == default_status.id
