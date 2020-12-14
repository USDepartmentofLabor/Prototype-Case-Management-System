from factory import SubFactory, Faker
from factory.alchemy import SQLAlchemyModelFactory

from app import db, models


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class RoleFactory(BaseFactory):

    class Meta:
        model = models.Role

    name = "Base Role"
    default = False
    permissions = 0


class UserFactory(BaseFactory):

    class Meta:
        model = models.User

    email = Faker('email')
    username = Faker('user_name')
    role = SubFactory(RoleFactory)


class CaseDefinitionFactory(BaseFactory):
    class Meta:
        model = models.CaseDefinition

    key = "TCD1"
    name = "Test Case Definition"


class ActivityDefinitionFactory(BaseFactory):
    class Meta:
        model = models.ActivityDefinition

    name = "Test Activity Definition"
    case_definition = SubFactory(CaseDefinitionFactory)
