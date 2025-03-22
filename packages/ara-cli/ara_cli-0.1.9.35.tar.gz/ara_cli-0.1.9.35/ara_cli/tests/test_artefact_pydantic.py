import pytest
from ara_cli.artefact_pydantic import TaskArtefact, FeatureArtefact, ArtefactType, Contribution, Scenario, ScenarioOutline, Example

# Test TaskArtefact


def test_task_artefact_from_text_basic():
    text = "@tag1 @tag2\nTask: Write code"
    task = TaskArtefact.from_text(text)
    assert task.tag == ["@tag1", "@tag2"]
    assert task.title == "Write code"
    assert task.description is None
    assert task.contribution is None
    assert task.free_contribution is None


def test_task_artefact_from_text_with_contribution():
    text = "@tag1\nTask: Improve performance\nContributes to F2 feature"
    task = TaskArtefact.from_text(text)
    assert task.tag == ["@tag1"]
    assert task.title == "Improve performance"
    assert task.contribution.artefact_identifier == "F2"
    assert task.contribution.category == "feature"


def test_task_artefact_from_text_invalid_no_tags():
    with pytest.raises(ValueError, match='Tag "Task:" should start with "@"'):
        TaskArtefact.from_text("Task: Do something")


def test_task_artefact_from_text_invalid_no_task():
    with pytest.raises(ValueError, match="No title found in task. Expected 'Task:' as start of the title"):
        TaskArtefact.from_text("@tag1\nDescription: Missing task")

# Test FeatureArtefact


def test_feature_artefact_serialize_basic():
    feature = FeatureArtefact(
        artefact_type=ArtefactType.feature,
        tag=["@feature1"],
        title="User Login",
        user="registered user",
        want_need="log into the system",
        goal="access my account",
        scenarios=[Scenario(title="Successful login", steps=[
                            "Given I am on the login page", "When I enter valid credentials", "Then I should be logged in"])]
    )
    expected = (
        "@feature1\n"
        "Feature: User Login\n"
        "  As a registered user\n"
        "  I want to log into the system\n"
        "  So that access my account\n"
        "  Scenario: Successful login\n"
        "    Given I am on the login page\n"
        "    When I enter valid credentials\n"
        "    Then I should be logged in"
    )
    assert feature.serialize() == expected


def test_feature_artefact_serialize_with_outline():
    feature = FeatureArtefact(
        artefact_type=ArtefactType.feature,
        tag=["@feature1"],
        title="User Login",
        user="registered user",
        want_need="log into the system",
        goal="access my account",
        scenarios=[ScenarioOutline(
            title="Login with different credentials",
            steps=["Given I am on the login page",
                   "When I enter <username> and <password>", "Then I should see <result>"],
            examples=[
                Example(title="Valid login", values={
                        "username": "user1", "password": "pass1", "result": "success"}),
                Example(title="Invalid login", values={
                        "username": "user2", "password": "wrong", "result": "failure"})
            ]
        )]
    )
    expected = (
        "@feature1\n"
        "Feature: User Login\n"
        "  As a registered user\n"
        "  I want to log into the system\n"
        "  So that access my account\n"
        "  Scenario Outline: Login with different credentials\n"
        "    Given I am on the login page\n"
        "    When I enter <username> and <password>\n"
        "    Then I should see <result>\n"
        "    Examples:\n"
        "      | descriptive scenario title | username | password | result  |\n"
        "      | Valid login                | user1    | pass1    | success |\n"
        "      | Invalid login              | user2    | wrong    | failure |"
    )
    assert feature.serialize() == expected


def test_feature_artefact_from_text_basic():
    text = (
        "@feature1\n"
        "Feature: User Login\n"
        "Contributes to F1 feature"
    )
    feature = FeatureArtefact.from_text(text)
    assert feature.tag == ["@feature1"]
    assert feature.title == "User Login"
    assert feature.contribution.artefact_identifier == "F1"
    assert feature.contribution.category == "feature"
    assert feature.description is None
    assert feature.user is None
    assert feature.want_need is None
    assert feature.goal is None
    assert feature.scenarios is None


def test_feature_artefact_from_text_with_outline():
    text = (
        "@feature1\n"
        "Feature: User Login\n"
        "Contributes to F1 feature"
    )
    feature = FeatureArtefact.from_text(text)
    assert feature.tag == ["@feature1"]
    assert feature.title == "User Login"
    assert feature.contribution.artefact_identifier == "F1"
    assert feature.contribution.category == "feature"
    assert feature.description is None
    assert feature.user is None
    assert feature.want_need is None
    assert feature.goal is None
    assert feature.scenarios is None


def test_feature_artefact_from_text_invalid_no_feature():
    with pytest.raises(ValueError, match="No title found in feature. Expected 'Feature:' as start of the title"):
        FeatureArtefact.from_text("@tag1\nAs a user")


def test_feature_artefact_from_text_incomplete_user_story():
    with pytest.raises(ValueError, match='Contributes to section shoud start with "Contributes to" symbol'):
        FeatureArtefact.from_text("@tag1\nFeature: Test\nAs a user")
