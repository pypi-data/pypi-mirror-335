from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.widgets import Button, Input, Label, LoadingIndicator, Static

from varcall.process.process_class import ProcessConfig
from varcall.components.file_suggester import file_suggester


class ProcessWidgets(Static):

    DEFAULT_CSS = """
    ProcessWidgets {
        width: 100%;
        height: auto;
        padding: 1;
    }

    ScrollableContainer {
        width: 100%;
        height: auto;
        margin: 0 1;
        border: tall $primary;
        background: $surface-darken-1;
    }

    .process-widget {
        layout: vertical;
        width: 100%;
        height: auto;
        min-height: 12;
        margin: 1 0;
        padding: 0 1;
    }

    .process-title {
        text-style: bold;
        background: $secondary-darken-1;
        color: $foreground;
        width: 100%;
        height: 3;
        content-align: center middle;
        border: tall $primary-darken-3;
    }

    .input-field {
        margin: 1 0;
        width: 1fr;
    }

    .process-description {
        padding: 1 2;
        width: 1fr;
    }

    .button-container {
        width: 100%;
        height: auto;
        margin: 1 0;
    }

    Input {
        margin: 0 1;
        width: 100%;
        border: tall $primary-darken-2;
        background: $surface-darken-2;
    }

    Input:focus {
        border: tall $accent;
    }

    Button {
        min-width: 16;
        background: $primary;
    }

    .action_buttons {
        margin-right: 1;
    }

    .view_results {
        background: $success-darken-1;
        margin: 0 1;
    }

    .view_results:hover {
        background: $success;
    }

    LoadingIndicator {
        width: 16;
        height: 3;
        display: none;
        margin: 1;
        color: $warning;
    }

    .running LoadingIndicator {
        display: block;
    }

    ScrollableContainer:focus-within {
        border: tall $accent;
    }

    ScrollableContainer.running {
        border: tall $warning;
    }
    """

    def __init__(self, processes: dict[str, ProcessConfig]):
        self.processes = processes
        super().__init__()

    def compose(self) -> ComposeResult:
        for config in self.processes.values():
            process_name = config.name.lower().replace(" ", "_")
            with ScrollableContainer(
                classes="process-widget", id=f"{process_name}_widget"
            ):
                # Title at top
                yield Label(config.display_name, classes="process-title")

                # Input fields in middle
                for field in config.input_fields:
                    yield Input(
                        placeholder=field.replace("_", " ").title(),
                        id=f"{process_name}_{field}_input",
                        suggester=file_suggester,
                        classes="input-field",
                    )

                # Button container for horizontal alignment
                with Horizontal(classes="button-container"):
                    # Description
                    if config.description:
                        yield Label(f"[orange]Description:[/orange] {config.description}", classes="process-description")

                    yield LoadingIndicator(id=f"{process_name}_loading")

                    # Process button
                    yield Button(
                        config.display_name,
                        id=f"{process_name}_button",
                        classes="action_buttons",
                    )

                    # View results button (only for processes that generate viewable results)
                    if process_name in ["fastqc", "multiqc", "bcftools_stats"]:
                        yield Button(
                            "View Results",
                            id=f"view_{process_name}_results",
                            classes="view_results",
                        )
