from flask import current_app
from app import models
from ..email import send_email

"""
Module containing functions to send notifications. Implemented as a module instead of class
because so far all the methods would be static.
"""


def notify_assignable_permission_removed_from_role(role: models.Role, cases):
    """
    Notifies admin users
        * that the assignable permission was removed from a role
        * which case have been assigned as a result
    :param role: The role whose permissions were changed
    :param cases: The cases that were affected by the change
    :return:
    """
    current_app.logger.info(f"notify role {role.name} was changed, affecting {len(cases)} cases")
    admin_role = models.Role.query.filter_by(name='Admin').first()
    for user in admin_role.users:
        if user.is_active:
            send_email(user.email, 'Assignable permission removed from role',
                       'roles/email/assign_perm_removed_from_role', web_app_url=current_app.config['WEB_APP_URL'],
                       user=user, role=role, cases=cases)


def notify_user_role_changed_not_assignable(user: models.User, cases):
    """
    Notifies admin users
        * that a user's role was changed from one with assignable permission to one without
        * the list of cases this affects
    :param user: the user whose role was changed
    :param cases: the list of cases the change affects
    :return:
    """
    current_app.logger.info(
        f"notify {user.name} role was changed from one with assignable perm to one without, affecting {len(cases)}")
    admin_role = models.Role.query.filter_by(name='Admin').first()
    for admin_user in admin_role.users:
        if admin_user.is_active:
            send_email(admin_user.email, 'User role changed from one with assignable permission to one without',
                       'users/email/role_changed_to_not_assignable', web_app_url=current_app.config['WEB_APP_URL'],
                       user=admin_user, changed_role_user=user, cases=cases)


def notify_role_deleted_with_assigned_permission(role: models.Role, cases):
    """
    Notifies admin users
        * that a role with ASSIGNABLE_TO_CASE permission was deleted and the "default" role does
          not have the permission
        * which cases we unassigned because of the change.
    :param role: role that was deleted
    :param cases: list of cases that were unassigned
    """
    current_app.logger.info(f"the role {role.name} was deleted, affecting {len(cases)} cases")
    admin_role = models.Role.query.filter_by(name='Admin').first()
    for user in admin_role.users:
        if user.is_active:
            send_email(user.email, 'Role with assign to case permission deleted',
                       'roles/email/role_deleted_with_assign_perm', web_app_url=current_app.config['WEB_APP_URL'],
                       user=user, role=role, cases=cases)


def notify_user_they_were_assigned_a_case(case: models.Case):
    """
    Notifies a user they were assigned to a case. The user will be the case.assigned_to
    property.
    :param case: The case the user was assigned to.
    """
    current_app.logger.info(f"notify {case.assigned_to.name} they were assigned to the '{case.name}' case")

    send_email(case.assigned_to.email, 'Case Assigned',
               'cases/email/case_assigned', web_app_url=current_app.config['WEB_APP_URL'], user=case.assigned_to,
               case=case)
