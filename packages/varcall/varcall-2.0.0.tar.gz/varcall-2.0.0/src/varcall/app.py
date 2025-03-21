from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import ( Button, Footer, Header, MarkdownViewer,
                              TabbedContent, TabPane,
                            )

from varcall.components.input_block import ProcessWidgets
from varcall.components.yes_or_no import YesOrNo
from varcall.process.process_class import Process
from varcall.process.process_dict import ( BCFTOOLS_PROCESS, GATK_PROCESS,
                                           HOME_PROCESSES, PIPLELINES,
                                           SAMTOOLS_PROCESSES,
                                          )
from varcall.help import help_path


class Varcall(App[None]):
    # Key bindings for the application
    BINDINGS = [
        ("f1", "show_help", "Help"),
        ("Q", "exit_app", "Exit App"),
        ("T", "change_theme", "Change Theme"),
        ("P", "print_theme_data", "Print Theme data"),
    ]

    CSS_PATH = "./app.css"

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="ScrollableContainer"):
            yield Header()
            yield Footer(show_command_palette=True)
            with TabbedContent():
                with TabPane("Home", id="HomeTab"):
                    yield ProcessWidgets(HOME_PROCESSES)
                with TabPane("Samtools", id="SamtoolsTab"):
                    yield ProcessWidgets(SAMTOOLS_PROCESSES)
                with TabPane("Bcftools", id="BcftoolsTab"):
                    yield ProcessWidgets(BCFTOOLS_PROCESS)
                with TabPane("GATK", id="GATKTab"):
                    yield ProcessWidgets(GATK_PROCESS)
                with TabPane("Pipeline", id="Pipeline"):
                    yield ProcessWidgets(PIPLELINES)
                with TabPane("Help", id="HelpTab"):
                    yield MarkdownViewer(Path(help_path).read_text())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id and button_id.endswith("_button"):
            process_name = button_id.replace("_button", "")
            if process_name in HOME_PROCESSES:
                Process(self, HOME_PROCESSES[process_name]).run()

    # Confirm exit application
    def maybe_exit_app(self, bool) -> None:
        if bool:
            self.exit()

    def action_exit_app(self) -> None:
        self.push_screen(
            YesOrNo("Do you want to exit application?"), self.maybe_exit_app
        )

    # Handels the key press for Toggle dark mode
    def action_change_theme(self) -> None:
        self.search_themes()

    # Handels the key press for Show help action
    def action_show_help(self) -> None:
        self.query_one(TabbedContent).active = "HelpTab"

    def action_print_theme_data(self):
        with open("themes.txt", "a") as f:
            f.write(f"\n\n{self.app.theme}\n\n")
            for key, value in self.app.theme_variables.items():
                f.write(f"{key}: {value}\n")


# Main entry point of the application
def main():
    Varcall().run()


if __name__ == "__main__":
    main()
