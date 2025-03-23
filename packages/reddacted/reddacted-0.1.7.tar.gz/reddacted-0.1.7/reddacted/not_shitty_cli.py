from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal, Container
from textual.widgets import Input, Switch, Label, Button
from textual.validation import Number
from dataclasses import dataclass
from typing import List, Optional

# Import styles from styles.py
from styles import TEXTUAL_CSS


@dataclass
class ConfigItem:
    id: str
    label: str
    widget_type: str
    placeholder: Optional[str] = None
    value: Optional[str] = None
    password: bool = False
    validator: Optional[Number] = None
    arg_name: Optional[str] = None
    section_hint: Optional[str] = None


class ConfigScreen(VerticalScroll):
    def __init__(self, config_items: List[ConfigItem], **kwargs):
        super().__init__(**kwargs)
        self.config_items = config_items

    def compose(self) -> ComposeResult:
        current_section = None
        for item in self.config_items:
            if item.section_hint != current_section:
                current_section = item.section_hint
                yield Label(f"[bold]{current_section}[/]", classes="section-title")
            if item.widget_type == "input":
                yield Horizontal(
                    Label(item.label),
                    Input(
                        placeholder=item.placeholder,
                        value=item.value,
                        password=item.password,
                        validators=[item.validator] if item.validator else None,
                        id=item.id,
                    ),
                )
            elif item.widget_type == "switch":
                yield Horizontal(
                    Label(item.label),
                    Switch(value=False, id=item.id),
                )


class ConfigApp(App):
    CSS = TEXTUAL_CSS

    def __init__(self, config_items: List[ConfigItem], **kwargs):
        super().__init__(**kwargs)
        self.config_items = config_items

    def compose(self) -> ComposeResult:
        # Main container for the config screen and buttons
        yield Container(
            ConfigScreen(self.config_items, id="config-container"),
            Horizontal(
                Button("Save", id="save-btn", variant="primary"),
                Button("Cancel", id="cancel-btn", variant="error"),
                classes="button-container",
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self.save_config()
        elif event.button.id == "cancel-btn":
            self.exit()

    def save_config(self) -> None:
        config = {}
        for item in self.config_items:
            widget = self.query_one(f"#{item.id}")
            if isinstance(widget, Input):
                config[item.id] = widget.value
            elif isinstance(widget, Switch):
                config[item.id] = widget.value
        print("Saved Config:", config)
        self.exit()


def _create_config_items() -> List[ConfigItem]:
    """Create the list of configuration items."""
    return [
        # Query Target
        ConfigItem(
            id="query_type",
            label="Query Type",
            widget_type="input",
            placeholder="user or listing",
            value="user",
            section_hint="Query Target",
        ),
        ConfigItem(
            id="query_target",
            label="Target (username or subreddit/article_id)",
            widget_type="input",
            placeholder="Enter username or subreddit/article_id",
            value="",
            section_hint="Query Target",
        ),
        # Reddit Authentication
        ConfigItem(
            id="reddit_username",
            label="Reddit Username",
            widget_type="input",
            placeholder="Enter Reddit username (optional)",
            section_hint="Reddit Authentication",
        ),
        ConfigItem(
            id="reddit_password",
            label="Reddit Password",
            widget_type="input",
            placeholder="Enter Reddit password (optional)",
            password=True,
            section_hint="Reddit Authentication",
        ),
        ConfigItem(
            id="reddit_client_id",
            label="Reddit Client ID",
            widget_type="input",
            placeholder="Enter Reddit client ID (optional)",
            section_hint="Reddit Authentication",
        ),
        ConfigItem(
            id="reddit_client_secret",
            label="Reddit Client Secret",
            widget_type="input",
            placeholder="Enter Reddit client secret (optional)",
            password=True,
            section_hint="Reddit Authentication",
        ),
        ConfigItem(
            id="enable_auth",
            label="Enable Reddit API Authentication",
            widget_type="switch",
            section_hint="Reddit Authentication",
        ),
        # LLM Configuration
        ConfigItem(
            id="openai_key",
            label="OpenAI API Key",
            widget_type="input",
            placeholder="Enter OpenAI API key",
            password=True,
            section_hint="LLM Configuration",
        ),
        ConfigItem(
            id="local_llm",
            label="Local LLM Endpoint URL",
            widget_type="input",
            placeholder="http://localhost:11434",
            value="http://localhost:11434",
            section_hint="LLM Configuration",
        ),
        ConfigItem(
            id="openai_base",
            label="Custom OpenAI Base URL",
            widget_type="input",
            placeholder="https://api.openai.com/v1",
            value="https://api.openai.com/v1",
            section_hint="LLM Configuration",
        ),
        ConfigItem(
            id="model",
            label="Model Name",
            widget_type="input",
            placeholder="gpt-4",
            value="gpt-4",
            section_hint="LLM Configuration",
        ),
        # Analysis Options
        ConfigItem(
            id="disable_pii",
            label="Disable PII Detection",
            widget_type="switch",
            section_hint="Analysis Options",
        ),
        ConfigItem(
            id="pii_only",
            label="Show Only Comments with PII",
            widget_type="switch",
            section_hint="Analysis Options",
        ),
        ConfigItem(
            id="limit",
            label="Comment Limit (0 = unlimited)",
            widget_type="input",
            placeholder="100",
            value="100",
            validator=Number(minimum=0),
            section_hint="Analysis Options",
        ),
        ConfigItem(
            id="batch_size",
            label="Batch Size",
            widget_type="input",
            placeholder="10",
            value="10",
            validator=Number(minimum=1),
            section_hint="Analysis Options",
        ),
        # Content Filtering
        ConfigItem(
            id="text_match",
            label="Text Match Pattern",
            widget_type="input",
            placeholder="Filter comments containing text",
            section_hint="Content Filtering",
        ),
        ConfigItem(
            id="skip_text",
            label="Skip Text Pattern",
            widget_type="input",
            placeholder="Exclude comments containing text",
            section_hint="Content Filtering",
        ),
        # Output
        ConfigItem(
            id="output_file",
            label="Output File",
            widget_type="input",
            placeholder="Path to save detailed results",
            section_hint="Output",
        ),
    ]


if __name__ == "__main__":
    config_items = _create_config_items()
    app = ConfigApp(config_items)
    app.run()
