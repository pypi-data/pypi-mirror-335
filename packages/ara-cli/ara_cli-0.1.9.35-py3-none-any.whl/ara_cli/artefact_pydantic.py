from pydantic import BaseModel, Field
from typing import Optional, List, Union, Dict
from enum import Enum
import re


class ArtefactType(str, Enum):
    feature = "feature"
    task = "task"
    example = "example"


class Contribution(BaseModel):
    artefact_identifier: str
    category: str
    rule: Optional[str] = None


class Example(BaseModel):
    title: Optional[str] = None
    values: Dict[str, str]


class Scenario(BaseModel):
    title: str
    steps: List[str]


class ScenarioOutline(BaseModel):
    title: str
    steps: List[str]
    examples: List[Example]


class Artefact(BaseModel):
    """Base artefact class with common fields"""
    artefact_type: ArtefactType
    # Still a list of strings, but serialized/deserialized as space-separated
    tag: List[str] = Field(
        default=[],
        description="Optional list of to-do flags (0-many)",
        # pattern=r'(@[A-Z]*[a-z]+)(_{0,1}([A-Z]*[a-z]+)?)*\w'
    )
    title: str = Field(
        description="Descriptive Artefact title (mandatory)",

    )
    contribution: Optional[Contribution] = Field(
        default=None,
        description="Artefact details to which this task contributes"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional further description to understand the task"
    )

    @classmethod
    def from_text(cls, text: str) -> 'Artefact':
        raise NotImplementedError("Subclasses must implement from_text")

    def _serialize_contribution(self) -> str:
        """Serialize the contribution field into the 'Contributes to' format."""
        if self.contribution:
            line = f"Contributes to {self.contribution.artefact_identifier} {self.contribution.category}"
            if self.contribution.rule:
                line += f" using rule {self.contribution.rule}"
            return line
        return ""

    @property
    def get_contributes_to(self) -> Optional[Contribution]:
        return self.contribution

    @property
    def get_description(self) -> Optional[str]:
        return self.description


class TaskArtefact(Artefact):
    free_contribution: Optional[str] = None
    action_items: List[str] = Field(default_factory=list)

    @classmethod
    def from_text(cls, text: str) -> 'TaskArtefact':
        import re
        from typing import List, Optional
        from pydantic import Field

        lines = [line.strip()
                 for line in text.strip().splitlines() if line.strip()]
        if not lines:
            raise ValueError("Empty artefact text")

        # Parse tags
        tags = lines[0].split()
        for tag in tags:
            if not tag.startswith('@'):
                raise ValueError(f'Tag "{tag}" should start with "@"')

        # Parse title
        if not lines[1].startswith("Task:"):
            raise ValueError(
                "No title found in task. Expected 'Task:' as start of the title")
        title = lines[1][len("Task:"):].strip()

        idx = 2
        contribution = None
        description = None
        action_items = []

        # Parse contribution (optional)
        if idx < len(lines):
            line = lines[idx]
            if line.startswith("Contributes to "):
                contrib_line = line
                expected_start = "Contributes to"
                contrib_text = contrib_line[len(expected_start):].strip()
                known_categories = ["feature", "task", "epic",
                                    "userstory", "keyfeature", "example", "capability"]
                if " using rule " in contrib_text:
                    identifier_category_text, rule_text = contrib_text.split(
                        " using rule ", 1)
                    rule = rule_text.strip()
                else:
                    identifier_category_text = contrib_text
                    rule = None
                parts = identifier_category_text.split()
                if len(parts) < 2:
                    raise ValueError(
                        'The artefact classifier for "Contributes to" section is not specified')
                for i in range(len(parts) - 1, -1, -1):
                    if parts[i].lower() in known_categories:
                        category = parts[i].lower()
                        identifier = " ".join(parts[:i])
                        break
                else:
                    raise ValueError(
                        'The artefact classifier for "Contributes to" section is not specified')
                if category == "task":
                    raise ValueError(
                        "It is not allowed to contribute to a task")
                if rule and category not in ["epic", "userstory"]:
                    raise ValueError(
                        "Using keyword only allowed to Epic and Userstory artefacts")
                contribution = Contribution(
                    artefact_identifier=identifier, category=category, rule=rule)
                idx += 1
            elif line.startswith("Contributes to:"):
                raise ValueError(
                    'Contributes to section should not include ":" symbol')
            # Optional: Handle other malformed contributions
            elif "Contributes" in line:
                raise ValueError(
                    'Contributes to section should start with "Contributes to "')

        # Parse description (optional)
        if idx < len(lines) and lines[idx].startswith("Description:"):
            description = lines[idx][len("Description:"):].strip()
            idx += 1

        # Parse action items (optional)
        while idx < len(lines):
            line = lines[idx]
            if line.startswith("[@"):
                match = re.match(r'\[@(\w+)\]', line)
                if match:
                    status = match.group(1)
                    if status not in ["to-do", "in-progress", "done"]:
                        raise ValueError(
                            f'Action item "@{status}" status not defined. Allowed action item statuses: "@to-do", "@in-progress", "@done"'
                        )
                    action_items.append(line)
                else:
                    raise ValueError(
                        "Invalid action item format. Expected [@status] followed by description")
            elif line.startswith("<@"):
                raise ValueError(
                    'Action item defined with "<>" notation. Action items should start with [@status]')
            elif line.startswith("[#"):
                raise ValueError(
                    'Action item defined with "#" notation. Action items should start with [@status]')
            else:
                raise ValueError(
                    "Invalid line after description. Expected action items starting with [@status]")
            idx += 1

        return cls(
            artefact_type=ArtefactType.task,
            tag=tags,
            title=title,
            contribution=contribution,
            description=description,
            action_items=action_items
        )


class FeatureArtefact(Artefact):
    user: str = Field(default=None)
    want_need: str = Field(default=None)
    goal: str = Field(default=None)
    scenarios: List[Union[Scenario, ScenarioOutline]] = Field(default=None)

    def serialize(self) -> str:
        """Serialize the FeatureArtefact into its text format with tags on one line."""
        lines = []
        # Join tags with spaces into a single line
        lines.append(" ".join(self.tag))
        lines.append(f"Feature: {self.title}")
        lines.append(f"  As a {self.user}")
        lines.append(f"  I want to {self.want_need}")
        lines.append(f"  So that {self.goal}")

        # Add contribution if present
        if self.contribution:
            lines.append(f"  {self._serialize_contribution()}")

        # Add description if present
        if self.description:
            lines.append(f"  Description: {self.description}")

        # Serialize scenarios
        for scenario in self.scenarios:
            lines.append(self._serialize_scenario(scenario))

        return "\n".join(lines)

    def _serialize_scenario(self, scenario: Union[Scenario, ScenarioOutline]) -> str:
        """Helper method to dispatch scenario serialization."""
        if isinstance(scenario, Scenario):
            return self._serialize_regular_scenario(scenario)
        elif isinstance(scenario, ScenarioOutline):
            return self._serialize_scenario_outline(scenario)
        else:
            raise ValueError("Unknown scenario type")

    def _serialize_regular_scenario(self, scenario: Scenario) -> str:
        """Serialize a regular Scenario."""
        lines = []
        lines.append(f"  Scenario: {scenario.title}")
        for step in scenario.steps:
            lines.append(f"    {step}")
        return "\n".join(lines)

    def _serialize_scenario_outline(self, scenario: ScenarioOutline) -> str:
        """Serialize a ScenarioOutline with aligned examples."""
        lines = []
        lines.append(f"  Scenario Outline: {scenario.title}")
        for step in scenario.steps:
            lines.append(f"    {step}")
        if scenario.examples:
            placeholders = self._extract_placeholders(scenario.steps)
            headers = ["descriptive scenario title"] + placeholders
            rows = [headers]
            for example in scenario.examples:
                row = [example.title or ""] + \
                    [str(example.values.get(ph, "")) for ph in placeholders]
                rows.append(row)
            # Calculate column widths
            column_widths = [max(len(str(row[i])) for row in rows)
                             for i in range(len(row))]
            column_widths = [max(len(str(row[i]))
                                 for i in range(len(headers))) for row in rows]
            column_widths = [max(len(str(row[i])) for row in rows)
                             for i in range(len(headers))]
            # Build formatted rows
            formatted_rows = []
            for row in rows:
                padded = [str(cell).ljust(width)
                          for cell, width in zip(row, column_widths)]
                formatted_rows.append("| " + " | ".join(padded) + " |")
            lines.append("    Examples:")
            for fr in formatted_rows:
                lines.append(f"      {fr}")
        return "\n".join(lines)

    def _extract_placeholders(self, steps):
        placeholders = []
        for step in steps:
            found = re.findall(r'<([^>]+)>', step)
            for ph in found:
                if ph not in placeholders:
                    placeholders.append(ph)
        return placeholders

    @classmethod
    def from_text(cls, text: str) -> 'FeatureArtefact':
        lines = [line.strip()
                 for line in text.strip().splitlines() if line.strip()]
        if not lines:
            raise ValueError("Empty artefact text")

        # Parse tags
        tags = lines[0].split()
        for tag in tags:
            if not tag.startswith('@'):
                raise ValueError(
                    f'Tag "{tag}" should start with "@" notation but started with "{tag[0]}"')
            if '@' in tag[1:]:
                raise ValueError(
                    f'Tag "{tag}" use "@" but this is not allowed as part of a tag name')

        # Parse title (existing validation assumed correct)
        feature_idx = next((i for i, line in enumerate(
            lines) if line.startswith('Feature:')), -1)
        if feature_idx == -1 or feature_idx != 1:
            raise ValueError(
                "No title found in feature. Expected 'Feature:' as start of the title")
        title_line = lines[feature_idx]
        title = title_line[len('Feature:'):].strip()
        if any(char in title for char in ['%', '&']):
            raise ValueError(
                "Artefact titles should not include these symbols: % &")

        # Parse contribution
        contrib_line = lines[2] if len(lines) > 2 else ""
        expected_start = "Contributes to"
        contribution = None
        if contrib_line:
            if contrib_line.startswith("Contributes to:"):
                raise ValueError(
                    'Contributes to section should not include ":" symbol')
            if not contrib_line.startswith(expected_start + " "):
                if contrib_line.startswith("Illustrates"):
                    raise ValueError(
                        'This feature artefact has "Illustrates". Only Example Artefact has Illustrates section')
                raise ValueError(
                    f'Contributes to section shoud start with "Contributes to" symbol')
            contrib_text = contrib_line[len(expected_start):].strip()

            known_categories = ["feature", "task", "epic",
                                "userstory", "keyfeature", "example", "capability"]
            if " using rule " in contrib_text:
                identifier_category_text, rule_text = contrib_text.split(
                    " using rule ", 1)
                rule = rule_text.strip()
            else:
                identifier_category_text = contrib_text
                rule = None

            parts = identifier_category_text.split()
            if len(parts) < 2:
                raise ValueError(
                    'The artefact classifier for "Contributes to" sction is not specified')
            for i in range(len(parts) - 1, -1, -1):
                if parts[i].lower() in known_categories:
                    category = parts[i].lower()
                    identifier = " ".join(parts[:i])
                    break
            else:
                raise ValueError(
                    'The artefact classifier for "Contributes to" sction is not specified')

            if category == "task":
                raise ValueError("It is not allowd to contribute to a task")
            if rule and category not in ["epic", "userstory"]:
                raise ValueError(
                    "Using keyword only allowed to Epic and Userstory artefacts")

            contribution = Contribution(
                artefact_identifier=identifier, category=category, rule=rule)

        # Parse description (optional, simplified)
        description = None
        if len(lines) > 3 and lines[3].startswith("Description:"):
            description = lines[3][len("Description:"):].strip()

        return cls(
            artefact_type=ArtefactType.feature,
            tag=tags,
            title=title,
            contribution=contribution,
            description=description
        )


class ExampleArtefact(Artefact):
    @classmethod
    def from_text(cls, text: str) -> 'ExampleArtefact':
        lines = [line.strip()
                 for line in text.strip().splitlines() if line.strip()]
        if not lines:
            raise ValueError("Empty artefact text")

        # Parse tags
        tags = lines[0].split()
        for tag in tags:
            if not tag.startswith('@'):
                raise ValueError(f'Tag "{tag}" should start with "@"')

        # Parse title
        if not lines[1].startswith("Example:"):
            raise ValueError("Title must start with 'Example:'")
        title = lines[1][len("Example:"):].strip()

        # Parse contribution
        contrib_line = lines[2] if len(lines) > 2 else ""
        expected_start = "Illustrates"
        if not contrib_line.startswith(expected_start + " "):
            if contrib_line.startswith("Contributes to"):
                raise ValueError(
                    "Example artefacts does not have Contributes to section")
            raise ValueError(
                f'Illustrates section shoud start with "Illustrates" symbol')
        contrib_text = contrib_line[len(expected_start):].strip()
        if ":" in contrib_text:
            raise ValueError(
                'Illustrates section should not include ":" symbol')

        known_categories = ["feature", "task", "epic",
                            "userstory", "keyfeature", "example", "capability"]
        if " using rule " in contrib_text:
            identifier_category_text, rule_text = contrib_text.split(
                " using rule ", 1)
            rule = rule_text.strip()
        else:
            identifier_category_text = contrib_text
            rule = None

        parts = identifier_category_text.split()
        if len(parts) < 2:
            raise ValueError(
                'The artefact classifier for "Illustrates" sction is not specified')
        for i in range(len(parts) - 1, -1, -1):
            if parts[i].lower() in known_categories:
                category = parts[i].lower()
                identifier = " ".join(parts[:i])
                break
        else:
            raise ValueError(
                'The artefact classifier for "Illustrates" sction is not specified')

        if category == "task":
            raise ValueError("It is not allowd to contribute to a task")
        if rule and category not in ["epic", "userstory"]:
            raise ValueError(
                "Using keyword only allowed to Epic and Userstory artefacts")

        contribution = Contribution(
            artefact_identifier=identifier, category=category, rule=rule)

        # Parse description (optional)
        description = None
        if len(lines) > 3 and lines[3].startswith("Description:"):
            description = lines[3][len("Description:"):].strip()

        return cls(
            artefact_type=ArtefactType.example,
            tag=tags,
            title=title,
            contribution=contribution,
            description=description
        )

# Helper functions for scenario parsing


def parse_scenario(lines: List[str], start_idx: int) -> tuple[Scenario, int]:
    """Parse a regular scenario block."""
    title = lines[start_idx][len('Scenario:'):].strip()
    steps = []
    idx = start_idx + 1
    while idx < len(lines) and not (lines[idx].startswith('Scenario:') or lines[idx].startswith('Scenario Outline:')):
        steps.append(lines[idx])
        idx += 1
    return Scenario(title=title, steps=steps), idx


def parse_scenario_outline(lines, start_idx):
    title = lines[start_idx][len('Scenario Outline:'):].strip()
    idx = start_idx + 1
    steps = []
    examples = []

    # Parse steps
    while idx < len(lines) and not lines[idx].strip().startswith('Examples:'):
        if lines[idx].strip():
            steps.append(lines[idx].strip())
        idx += 1

    # Parse examples
    if idx < len(lines) and lines[idx].strip() == 'Examples:':
        idx += 1
        headers = [h.strip() for h in lines[idx].split('|') if h.strip()]
        idx += 1
        while idx < len(lines) and lines[idx].strip():
            row = [cell.strip()
                   for cell in lines[idx].split('|') if cell.strip()]
            example_title = row[0] if headers[0] == 'descriptive scenario title' else None
            values = dict(zip(headers[1:], row[1:])) if example_title else dict(
                zip(headers, row))
            examples.append(Example(title=example_title, values=values))
            idx += 1

    return ScenarioOutline(title=title, steps=steps, examples=examples), idx


'''
# Structured contribution task
task1 = TaskArtefact(
    artefact_type=ArtefactType.task,
    tag=["@to-do"],
    title="Implement login feature",
    contribution=Contribution(
        artefact_identifier="auth_module.py",
        category="feature",
        rule="must use OAuth"
    ),
    description="Add login functionality with OAuth support."
)

serialized_task1 = task1.serialize()

print(serialized_task1)


deserialized_task1 = TaskArtefact.from_text(serialized_task1)
print(deserialized_task1)
print(deserialized_task1.title)
print(deserialized_task1.description)


# Task artefact example
task_text = """
@to-do @user_Ahmet
Task: Review code
Just a general code review
"""
task = TaskArtefact.from_text(task_text)
print(task.title)  # "Review code"
print(task.tag)
print(task.free_contribution)  # "Just a general code review"

# Feature artefact example
feature_text = """
@sample_tag
Feature: User authentication

  As a registered user
  I want to log in with my credentials
  So that access my account securely

  Scenario: Successful login
    Given a registered user
    When they enter valid credentials
    Then they are logged in
"""
feature = FeatureArtefact.from_text(feature_text)
print(feature.title)  # "User authentication"
print(feature.user)  # "registered user"
print(feature.scenarios[0].title)  # "Successful login"


# Free task
task2 = TaskArtefact(
    artefact_type=ArtefactType.task,
    tag=["@to-do"],
    title="Review code",
    free_contribution="Just a general code review",
)
print(task2.serialize())


feature = FeatureArtefact(
    artefact_type=ArtefactType.feature,
    tag=["@sample_tag"],
    title="User authentication",
    user="registered user",
    want_need="log in with my credentials",
    goal="access my account securely",
    contribution=Contribution(
        artefact_identifier="security_spec",
        category="specification"
    ),
    description="Support secure login.",
    scenarios=[
        Scenario(
            title="Successful login",
            steps=[
                "Given a registered user",
                "When they enter valid credentials",
                "Then they are logged in"
            ]
        ),
        ScenarioOutline(
            title="Login attempts",
            steps=[
                "Given a user with <status>",
                "When they attempt to log in with <credentials>",
                "Then they see <result>"
            ],
            examples=[
                Example(title="valid login", values={
                        "status": "registered", "credentials": "valid", "result": "success"}),
                Example(title="invalid login", values={
                        "status": "registered", "credentials": "invalid", "result": "error"})
            ]
        )
    ]
)
print(feature.serialize())
'''
