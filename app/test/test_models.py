# pylint: disable=redefined-outer-name
"""Test that all models are imported in __init__.py.""" ""
import glob
import os
from datetime import datetime
from typing import Any

import pytest
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api import models as model_init
from app.api.models.account_models import Account, Auth
from app.api.models.budget_expenditure_models import Budget, Expenditure
from app.api.models.gift_models import Gift
from app.api.models.meal_models import Meal, MealCategory, MealTag
from app.api.models.organization_models import (
    Organization,
    OrganizationDetail,
    OrganizationMember,
    OrganizationRole,
    OrganizationTag,
)
from app.api.models.role_permission_models import Permission, RolePermission
from app.database.connection import Base

DATABASE_URL = config("DATABASE_URL", default="sqlite:///test.db")

print(DATABASE_URL)
ACCOUNT_ID = "kjwlk324bknb2l3kj4g23k4j2h34k23g2k34g23"
account = Account(
    id=ACCOUNT_ID,
    first_name="John",
    last_name="Doe",
    email="test@email.com",
    password_hash="password",
    phone_number="1234567890",
    is_verfiied=False,
    is_2fa_enabled=False,
    is_deleted=False,
)

AUTH_ID = "dfljhesrwerwernbwermnwermwerbwmtenwrwrj234i4534b4"
auth = Auth(
    id=AUTH_ID, account_id=ACCOUNT_ID, provider="google", account=account
)

PERMISSION_ID = "3kjbk34jh34k5j345k3jg53k5jh3g5k34j5hge3k543j45gk35"
permission = Permission(
    id=PERMISSION_ID,
    name="Test Permission",
    description="Test Description",
    is_deleted=False,
)

ORGANIZATION_ID = "23nbm4h5m45345345jgm34535gk34j5g3k4j5g34"
organization = Organization(
    id=ORGANIZATION_ID,
    owner=account.id,
    name="Test Organization",
    is_deleted=False,
    org_type="Wedding",
)

ORGANIZATION_DETAIL_ID = 1
organization_detail = OrganizationDetail(
    id=ORGANIZATION_DETAIL_ID,
    organization_id=ORGANIZATION_ID,
    event_location="Test Location",
    website="www.test.com",
    event_start_time=datetime.strptime(
        "2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
    ),
    event_end_time=datetime.strptime(
        "2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
    ),
    event_date=datetime.strptime("2021-01-01", "%Y-%m-%d"),
)

ORGANIZATION_ROLE_ID = "34bv45b6v6mmv3h456456bv54mn6b6v645v"
organization_role = OrganizationRole(
    id=ORGANIZATION_ROLE_ID,
    organization_id=ORGANIZATION_ID,
)

ROLE_PERMISSION_ID = "3kjbk34jh34k5j345k3jg53k5jwh3g5k34j5hg3k543j45gk35"
role_permission = RolePermission(
    id=ROLE_PERMISSION_ID,
    role_id=ORGANIZATION_ROLE_ID,
    permission_id=PERMISSION_ID,
)

ORGANIZATION_MEMBER_ID = 1
organization_member = OrganizationMember(
    id=ORGANIZATION_MEMBER_ID,
    organization_id=ORGANIZATION_ID,
    account_id=ACCOUNT_ID,
    organization_role_id=ORGANIZATION_ROLE_ID,
    organization=organization,
    account=account,
    member_role=organization_role,
)

ORGANIZATION_TAG_ID = "vm64n5v36jh5v63jh6mn3456vmn3vmn5b63m45nv"
organization_tag = OrganizationTag(
    id=ORGANIZATION_TAG_ID,
    organization_id=ORGANIZATION_ID,
    name="Test Tag",
    description="Test Description",
    tag_type="guest",
)

MEAL_CATEGORY_ID = "3kjbk34jh34k5j345k3jg53k5jh3g5k34j5hg3k543j45gk35"
meal_category = MealCategory(
    id=MEAL_CATEGORY_ID,
    name="Test Meal Category",
    organization_id=ORGANIZATION_ID,
    is_hidden=False,
)

MEAL_ID = "3kjbk34jh34k5j345k3jg53k5jh3rg5k34j5hg3k543j45gk35"
meal = Meal(
    id=MEAL_ID,
    name="Test Meal",
    description="Test Description",
    image_url="www.test.com",
    meal_category_id=MEAL_CATEGORY_ID,
    is_hidden=False,
    quantity=1,
)

MEAL_TAGS_ID = "3kjbk34jh34k5j345k3jg53k5jh3g5k34j5hg3k543j45gk35d"
meal_tags = MealTag(
    id=MEAL_TAGS_ID,
    organization_tag_id=ORGANIZATION_TAG_ID,
    meal_id=MEAL_ID,
)

BUDGET_ID = "3kjbk34jh34k5j345k3jg53k5jh3g5k34j5hg3k543j45gk35f"
budget = Budget(
    id=BUDGET_ID,
    organization_id=ORGANIZATION_ID,
    title="Test Budget",
    currency="USD",
    amount=1000,
    description="Test Description",
)

EXPENDITURE_ID = "3kjbk34jh34k5j345k3jge53k5jh3g5k34j5hg3k543j45gk35"
expenditure = Expenditure(
    id=EXPENDITURE_ID,
    budget_id=budget.id,
    title="Test Expenditure",
    currency="USD",
    amount=1000,
    description="Test Description",
)

GIFT_ID = "3kjbk34jh34k5j345k3jg53k5jh3g5k34j5hg3k543j45gk35"
gift = Gift(
    id=GIFT_ID,
    organization_id=ORGANIZATION_ID,
    title="Test Gift",
    description="Test Description",
    product_unit_price=100,
    product_total_amount=100,
    product_quantity=1,
    product_url="www.test.com",
    product_image_url="www.test.com",
    currency="USD",
    payment_provider="paypal",
    payment_link="www.test.com",
    gift_type="physical",
    gift_amount_type="fixed",
    gift_status="available",
    is_gift_hidden=False,
    is_gift_amount_hidden=False,
)


@pytest.fixture()
def setup_module_fixture() -> Any:
    """Setup the database."""
    engine = create_engine(DATABASE_URL)
    testing_session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    Base.metadata.create_all(bind=engine)
    db = testing_session_local()

    try:
        yield db
    finally:
        db.close()
    return db


def test_all_models() -> None:
    """Test that all models are imported in __init__.py."""
    modules = glob.glob(
        os.path.join(os.path.dirname(model_init.__file__), "*.py")
    )
    all_models = [
        os.path.basename(f)[:-3]
        for f in modules
        if os.path.isfile(f) and not f.endswith("__init__.py")
    ]
    assert sorted(all_models) == sorted(model_init.__all__)


def test_account_model(
    setup_module_fixture: Any,
) -> None:
    """Test the account model."""
    db = setup_module_fixture
    db.add(account)
    db.commit()
    db.refresh(account)

    assert account.first_name == "John"
    assert account.last_name == "Doe"
    assert account.email == account.email
    assert account.password_hash == "password"
    assert account.is_verfiied is False
    assert account.is_2fa_enabled is False
    assert account.is_deleted is False


def test_auth_model(
    setup_module_fixture: Any,
) -> None:
    """Test the auth model."""
    db = setup_module_fixture
    db.add(auth)
    db.commit()
    db.refresh(auth)

    assert auth.account_id == account.id
    assert auth.provider == "google"


def test_account_auth_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the account auth relationship."""
    db = setup_module_fixture
    auth_instance = (
        db.query(Auth).filter(Auth.account_id == account.id).first()
    )

    assert auth_instance.account_id == account.id
    assert auth_instance.account.first_name == account.first_name


def test_permission_model(
    setup_module_fixture: Any,
) -> None:
    """Test the permission model."""
    db = setup_module_fixture
    db.add(permission)
    db.commit()
    db.refresh(permission)

    assert permission.name == "Test Permission"
    assert permission.description == "Test Description"
    assert permission.is_deleted is False


def test_role_permission_model(
    setup_module_fixture: Any,
) -> None:
    """Test the role_permission model."""
    db = setup_module_fixture
    db.add(role_permission)
    db.commit()
    db.refresh(role_permission)

    assert role_permission.role_id == organization_role.id
    assert role_permission.permission_id == permission.id


def test_role_permission_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the role_permission relationship."""
    db = setup_module_fixture
    role_permission_instance = (
        db.query(RolePermission)
        .filter(RolePermission.role_id == organization_role.id)
        .first()
    )

    assert role_permission_instance.role_id == organization_role.id
    assert role_permission_instance.role.name == organization_role.name
    assert role_permission_instance.permission_id == permission.id
    assert role_permission_instance.permission.name == permission.name


def test_organization_model(
    setup_module_fixture: Any,
) -> None:
    """Test the organization model."""
    db = setup_module_fixture
    db.add(organization)
    db.commit()
    db.refresh(organization)

    assert organization.name == "Test Organization"

    assert organization.is_deleted is False
    assert organization.org_type == "Wedding"


def test_organization_detail_model(
    setup_module_fixture: Any,
) -> None:
    """Test the organization_detail model."""
    db = setup_module_fixture
    db.add(organization_detail)
    db.commit()
    db.refresh(organization_detail)

    assert organization_detail.event_location == "Test Location"
    assert organization_detail.website == "www.test.com"
    assert organization_detail.event_start_time == datetime.strptime(
        "2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
    )
    assert organization_detail.event_end_time == datetime.strptime(
        "2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
    )
    assert organization_detail.event_date == datetime.strptime(
        "2021-01-01", "%Y-%m-%d"
    )


def test_organization_organization_detail_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the organization organization_detail relationship."""
    db = setup_module_fixture
    organization_instnace = (
        db.query(Organization)
        .filter(Organization.id == organization_detail.organization_id)
        .first()
    )

    assert organization_detail.organization_id == organization_instnace.id
    assert organization_detail.organization.name == organization_instnace.name


def test_organization_member_model(
    setup_module_fixture: Any,
) -> None:
    """Test the organization_member model."""
    db = setup_module_fixture
    db.add(organization_member)
    db.commit()
    db.refresh(organization_member)

    assert organization_member.organization_id == organization.id
    assert organization_member.account_id == account.id
    assert organization_member.organization_role_id == ORGANIZATION_ROLE_ID


def test_organization_role_model(
    setup_module_fixture: Any,
) -> None:
    """Test the organization_role model."""
    db = setup_module_fixture
    db.add(organization_role)
    db.commit()
    db.refresh(organization_role)

    assert organization_role.organization_id == organization.id


def test_organization_role_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the organization_role relationship."""
    db = setup_module_fixture
    organization_role_instance = (
        db.query(OrganizationRole)
        .filter(OrganizationRole.organization_id == organization.id)
        .first()
    )

    assert organization_role_instance.organization_id == organization.id
    assert organization_role_instance.organization.name == organization.name
    assert organization_role_instance.role_id == organization_role.id
    assert organization_role_instance.role.name == organization_role.name
    assert organization_role_instance.members[0].account_id == account.id


def test_organization_member_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the organization organization_member relationship."""
    db = setup_module_fixture
    organization_member_instance = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.organization_id == organization.id)
        .first()
    )

    assert organization_member_instance.organization_id == organization.id
    assert organization_member_instance.organization.name == organization.name
    assert organization_member_instance.account_id == account.id
    assert (
        organization_member_instance.account.first_name == account.first_name
    )
    assert organization_member_instance.member_role.id == organization_role.id


def test_organization_tag_model(
    setup_module_fixture: Any,
) -> None:
    """Test the organization_tag model."""
    db = setup_module_fixture
    db.add(organization_tag)
    db.commit()
    db.refresh(organization_tag)

    assert organization_tag.organization_id == organization.id
    assert organization_tag.name == "Test Tag"
    assert organization_tag.description == "Test Description"


def test_organization_tag_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the organization organization_tag relationship."""
    db = setup_module_fixture
    organization_tag_instance = (
        db.query(OrganizationTag)
        .filter(OrganizationTag.organization_id == organization.id)
        .first()
    )

    assert organization_tag_instance.organization_id == organization.id
    assert organization_tag_instance.organization.name == organization.name


def test_meal_category_model(
    setup_module_fixture: Any,
) -> None:
    """Test the meal_category model."""
    db = setup_module_fixture
    db.add(meal_category)
    db.commit()
    db.refresh(meal_category)

    assert meal_category.name == "Test Meal Category"
    assert meal_category.organization_id == organization.id
    assert meal_category.is_hidden is False


def test_meal_category_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the meal_category relationship."""
    db = setup_module_fixture
    meal_category_instance = (
        db.query(MealCategory)
        .filter(MealCategory.organization_id == organization.id)
        .first()
    )

    assert meal_category_instance.organization_id == organization.id
    assert meal_category_instance.organization.name == organization.name


def test_meal_model(
    setup_module_fixture: Any,
) -> None:
    """Test the meal model."""
    db = setup_module_fixture
    db.add(meal)
    db.commit()
    db.refresh(meal)

    assert meal.name == "Test Meal"
    assert meal.description == "Test Description"
    assert meal.image_url == "www.test.com"
    assert meal.meal_category_id == meal_category.id
    assert meal.is_hidden is False
    assert meal.quantity == 1


def test_meal_tag_model(
    setup_module_fixture: Any,
) -> None:
    """Test the meal_tag model."""
    db = setup_module_fixture
    db.add(meal_tags)
    db.commit()
    db.refresh(meal_tags)

    assert meal_tags.meal_id == meal.id
    assert meal_tags.organization_tag_id == organization_tag.id


def test_meal_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the meal relationship."""
    db = setup_module_fixture
    meal_instance = (
        db.query(Meal)
        .filter(Meal.meal_category_id == meal_category.id)
        .first()
    )

    assert meal_instance.meal_category_id == meal_category.id
    assert meal_instance.meal_categories.name == meal_category.name


def test_budget_model(
    setup_module_fixture: Any,
) -> None:
    """Test the budget model."""
    db = setup_module_fixture
    db.add(budget)
    db.commit()
    db.refresh(budget)

    assert budget.organization_id == organization.id
    assert budget.title == "Test Budget"
    assert budget.currency == "USD"
    assert budget.amount == 1000
    assert budget.description == "Test Description"


def test_expenditure_model(
    setup_module_fixture: Any,
) -> None:
    """Test the expenditure model."""
    db = setup_module_fixture
    db.add(expenditure)
    db.commit()
    db.refresh(expenditure)

    assert expenditure.budget_id == budget.id
    assert expenditure.title == "Test Expenditure"
    assert expenditure.currency == "USD"
    assert expenditure.amount == 1000
    assert expenditure.description == "Test Description"


def test_gift_model(
    setup_module_fixture: Any,
) -> None:
    """Test the gift model."""
    db = setup_module_fixture
    db.add(gift)
    db.commit()
    db.refresh(gift)

    assert gift.organization_id == organization.id
    assert gift.title == "Test Gift"
    assert gift.description == "Test Description"
    assert gift.product_unit_price == 100
    assert gift.product_total_amount == 100
    assert gift.product_quantity == 1
    assert gift.product_url == "www.test.com"
    assert gift.product_image_url == "www.test.com"
    assert gift.currency == "USD"
    assert gift.payment_provider == "paypal"
    assert gift.payment_link == "www.test.com"
    assert gift.gift_type == "physical"
    assert gift.gift_amount_type == "fixed"
    assert gift.gift_status == "available"
    assert gift.is_gift_hidden is False
    assert gift.is_gift_amount_hidden is False


def test_organization_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the organization relationship."""
    db = setup_module_fixture
    organization_instance = (
        db.query(Organization)
        .filter(Organization.id == organization_detail.organization_id)
        .first()
    )

    assert organization_instance.account.id == account.id
    assert organization_instance.detail[0].id == organization_detail.id
    assert organization_instance.tags[0].id == organization_tag.id
    assert (
        organization_instance.organization_members[0].id
        == organization_member.id
    )
    assert organization_instance.gifts[0].id == gift.id
    assert organization_instance.meal_categories[0].id == meal_category.id
    assert organization_instance.budget[0].id == budget.id


def test_budget_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the budget relationship."""
    db = setup_module_fixture
    budget_instnace = (
        db.query(Budget)
        .filter(Budget.organization_id == organization.id)
        .first()
    )

    assert budget_instnace.organization_id == organization.id
    assert budget_instnace.organization.name == organization.name


def test_expenditure_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the expenditure relationship."""
    db = setup_module_fixture
    expenditure_instance = (
        db.query(Expenditure)
        .filter(Expenditure.budget_id == budget.id)
        .first()
    )

    assert expenditure_instance.budget_id == budget.id
    assert expenditure_instance.budget.title == budget.title


def test_gift_realtionship(
    setup_module_fixture: Any,
) -> None:
    """Test the gift relationship."""
    db = setup_module_fixture
    gift_instance = (
        db.query(Gift).filter(Gift.organization_id == organization.id).first()
    )

    assert gift_instance.organization_id == organization.id
    assert gift_instance.organization.name == organization.name


def test_teradown_module() -> None:
    """Tear down the database."""
    print("Tearing down")
    os.remove("\test.db")
