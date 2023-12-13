from django.contrib.auth.models import Group, Permission
# -----------------------------------------------------------------------------------#
#                               Method for create groups
# -----------------------------------------------------------------------------------#
def create_groups():
    base_user, user_created = Group.objects.get_or_create(name="base_user")
    expert_user, expert_user_created = Group.objects.get_or_create(name="expert_user")

    # after the first start of the program, this printout must never be displayed
    if user_created or expert_user_created:
        print("creating groups for users ")
