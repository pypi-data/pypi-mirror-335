from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual import on


class YesOrNo(ModalScreen):
    CSS = """
        YesOrNo{
            width: auto;
            height: auto;
            align: center middle;
            Container{
                width: auto;
                align: center middle;
                height: auto;
                padding: 1 2;
                margin: 2;
                background: $panel;
                }
            Label{
                width: 100%;
                height: auto;
                margin: 1;
                content-align: center middle;
                align: center middle;
                }
            #horizontal_yesorno{
                width: auto;
                height: auto;
                margin: 1;
                Button{
                    margin: 0 1 0 0;
                    }
                }
            }"""

    def __init__(self, Title: str = "Yes or No") -> None:
        self.Title = Title
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(id="yesorno"):
            yield Label(self.Title)
            with Horizontal(id="horizontal_yesorno"):
                yield Button.success("Yes", id="yes")
                yield Button.error("No", id="no")

    @on(Button.Pressed)
    def close_modalscreen(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")
