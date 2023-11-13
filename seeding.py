# import uuid
# from datetime import datetime

# from app.api.models.account_models import Account, Auth
# from app.api.models.budget_expenditure_models import Budget, Expenditure
# from app.api.models.gift_models import Gift
# from app.api.models.meal_models import Meal, MealCategory, MealTag
# from app.api.models.organization_models import (
#     Organization,
#     OrganizationDetail,
#     OrganizationInvite,
#     OrganizationMember,
#     OrganizationRole,
#     OrganizationTag,
# )
# from app.api.models.role_permission_models import (
#     Permission,
#     Role,
#     RolePermission,
# )
# from app.database.connection import get_db_unyield

# # script to seed the database
# ACCOUNT_ID = "kjwlk324bknb2l3kj4g73k4j2h34k23g2k34g23"

# account = Account(
#     id=ACCOUNT_ID,
#     first_name="John",
#     last_name="Doe",
#     email="test@email.com",
#     password_hash="password",
#     phone_number="1234567890",
#     is_verfiied=False,
#     is_2fa_enabled=False,
#     is_deleted=False,
# )
# AUTH_ID = "dfljhesrwerwernbwermnwermwelbwjtenwrwrj234i4534b4"
# auth = Auth(
#     id=AUTH_ID, account_id=ACCOUNT_ID, provider="google", account=account
# )
# ROLE_ID = "3kjbk34jh34k5j345k3jg53k5jh3g5k3t4j5hg3k543j45gk35"
# role = Role(
#     id=ROLE_ID,
#     name="Test Role",
#     description="Test Description",
#     is_deleted=False,
# )
# PERMISSION_ID = "3kjbk34jh34k5j345k3jg53k5jh3g5k34j5hge3k543j45gk35"
# permission = Permission(
#     id=PERMISSION_ID,
#     name="Test Permission",
#     description="Test Description",
#     is_deleted=False,
# )
# ROLE_PERMISSION_ID = "3kjbk34jh34k5j345k3jg53k5jwh3g5k34j5hg3k543j45gk35"
# role_permission = RolePermission(
#     id=ROLE_PERMISSION_ID, role_id=ROLE_ID, permission_id=PERMISSION_ID
# )
# ORGANIZATION_ID = "23nbm4h5m45345345jgm34535gk34j5g3k4j5g34"
# organization = Organization(
#     id=ORGANIZATION_ID,
#     owner=account.id,
#     name="Test Organization",
#     is_deleted=False,
#     org_type="Wedding",
# )
# ORGANIZATION_DETAIL_ID = 1
# organization_detail = OrganizationDetail(
#     id=ORGANIZATION_DETAIL_ID,
#     organization_id=ORGANIZATION_ID,
#     event_location="Test Location",
#     website="www.test.com",
#     event_start_time=datetime.strptime(
#         "2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
#     ),
#     event_end_time=datetime.strptime(
#         "2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
#     ),
#     event_date=datetime.strptime("2021-01-01", "%Y-%m-%d"),
# )
# ORGANIZATION_ROLE_ID = "34bv45b6v6mmv3h456456bv54mn6b6v645v"
# organization_role = OrganizationRole(
#     id=ORGANIZATION_ROLE_ID,
#     organization_id=ORGANIZATION_ID,
#     role_id=ROLE_ID,
# )
# ORGANIZATION_MEMBER_ID = 1
# organization_member = OrganizationMember(
#     id=ORGANIZATION_MEMBER_ID,
#     organization_id=ORGANIZATION_ID,
#     account_id=ACCOUNT_ID,
#     organization_role_id=ROLE_ID,
#     organization=organization,
#     account=account,
#     member_role=organization_role,
# )
# ORGANIZATION_INVITE_ID = 1
# organization_invite = OrganizationInvite(
#     id=ORGANIZATION_INVITE_ID,
#     organization_id=ORGANIZATION_ID,
#     account_id=ACCOUNT_ID,
#     organization_member_id=ORGANIZATION_MEMBER_ID,
#     token="test_token",
#     status="pending",
# )
# ORGANIZATION_TAG_ID = "vm64n5v36jh5v63jh6mn3456vmn3vmn5b63m45nv"
# organization_tag = OrganizationTag(
#     id=ORGANIZATION_TAG_ID,
#     organization_id=ORGANIZATION_ID,
#     name="Test Tag",
#     description="Test Description",
#     tag_type="guest",
# )
# MEAL_CATEGORY_ID = "3kjbk34jh34k5j345k3jg53k5jh3g5k34j5hg3k543j45gk35"
# meal_category = MealCategory(
#     id=MEAL_CATEGORY_ID,
#     name="Test Meal Category",
#     organization_id=ORGANIZATION_ID,
#     is_hidden=False,
# )
# MEAL_ID = "3kjbk34jh34k5j345k3jg53k5jh3rg5k34j5hg3k543j45gk35"
# meal = Meal(
#     id=MEAL_ID,
#     name="Test Meal",
#     description="Test Description",
#     image_url="www.test.com",
#     meal_category_id=MEAL_CATEGORY_ID,
#     is_hidden=False,
#     quantity=1,
# )
# MEAL_TAGS_ID = "3kjbk34jh34k5j345k3jg53k5jh3g5k34j5hg3k543j45gk35d"
# meal_tags = MealTag(
#     id=MEAL_TAGS_ID,
#     organization_tag_id=ORGANIZATION_TAG_ID,
#     meal_id=MEAL_ID,
# )
# BUDGET_ID = "3kjbk34jh34k5j345k3jg53k5jh3g5k34j5hg3k543j45gk35f"
# budget = Budget(
#     id=BUDGET_ID,
#     organization_id=ORGANIZATION_ID,
#     title="Test Budget",
#     currency="USD",
#     amount=1000,
#     description="Test Description",
# )
# EXPENDITURE_ID = "3kjbk34jh34k5j345k3jge53k5jh3g5k34j5hg3k543j45gk35"
# expenditure = Expenditure(
#     id=EXPENDITURE_ID,
#     budget_id=budget.id,
#     title="Test Expenditure",
#     currency="USD",
#     amount=1000,
#     description="Test Description",
# )
# GIFT_ID = "3kjbk34jh34k5j345k3jg53k5jh3g5k34j5hg3k543j45gk35"
# gift = Gift(
#     id=GIFT_ID,
#     organization_id=ORGANIZATION_ID,
#     title="Test Gift",
#     description="Test Description",
#     product_unit_price=100,
#     product_total_amount=100,
#     product_quantity=1,
#     product_url="www.test.com",
#     product_image_url="www.test.com",
#     currency="USD",
#     payment_provider="paypal",
#     payment_link="www.test.com",
#     gift_type="physical",
#     gift_amount_type="fixed",
#     gift_status="available",
#     is_gift_hidden=False,
#     is_gift_amount_hidden=False,
# )
# with get_db_unyield() as db:
#     print("Hello World : !")

#     # db.add(account)
#     # db.commit()
#     # db.refresh(account)

#     organization = db.query(Account).filter_by(id=ACCOUNT_ID).first()

#     if organization:
#         print(f"Organization found: {organization.__dict__}")
#     else:
#         print(f"No organization found with id: {ORGANIZATION_ID}")

#     # db.add(account)
#     # db.add(auth)
#     # db.add(role)
#     # db.add(permission)
#     # db.add(role_permission)
#     # db.add(organization)
#     # db.add(organization_detail)
#     # db.add(organization_role)
#     # db.add(organization_member)
#     # db.add(organization_invite)
#     # db.add(organization_tag)
#     # db.add(meal_category)
#     # db.add(meal)
#     # db.add(meal_tags)
#     # db.add(budget)
#     # db.add(expenditure)
#     # db.add(gift)
#     # db.commit()
#     # db.refresh(account)
#     # db.refresh(auth)
#     # db.refresh(role)
#     # db.refresh(permission)
#     # db.refresh(role_permission)
#     # db.refresh(organization)
#     # db.refresh(organization_detail)
#     # db.refresh(organization_role)
#     # db.refresh(organization_member)
#     # print(db.query(OrganizationMember).filter_by
# (id=ORGANIZATION_MEMBER_ID))
#     # db.refresh(organization_invite)
#     # db.refresh(organization_tag)
#     # db.refresh(meal_category)
#     # db.refresh(meal)
#     # db.refresh(meal_tags)
#     # db.refresh(budget)
#     # db.refresh(expenditure)
#     # db.refresh(gift)

# print("Database seeded successfully")
