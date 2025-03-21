from pathlib import Path
import threading
import subprocess
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from textual.widgets import Input


@dataclass
class ProcessConfig:
    name: str
    command: str
    input_fields: List[str]
    required_fields: List[str]
    display_name: Optional[str] = None
    default_output_ext: str = ""
    description: str = ""
    success_message: str = ""
    error_message: str = ""

    def __post_init__(self):
        if self.display_name is None:
            self.display_name = self.name.replace("_", " ").title()


class Process:
    def __init__(self, app_instance: Any, config: ProcessConfig):
        self.app = app_instance
        self.config = config
        self.inputs: Dict[str, str] = {}
        self.outputs: Dict[str, str] = {}

    @property
    def all_fields(self) -> Dict[str, str]:
        """Return combined dictionary of inputs and outputs"""
        return {**self.inputs, **self.outputs}

    def _get_input(self, field) -> str:
        """Get input value from a form field"""
        process_name = self.config.name.lower().replace(" ", "_")
        return self.app.query_one(f"#{process_name}_{field}_input", Input).value.strip()

    def _get_all_fields_with_defaults(self, field) -> str:
        """Get field value with default fallback for empty values"""
        value = self._get_input(field)
        if not value:
            value = str(self.get_default_output_file())
        return value

    def validate_inputs(self) -> Tuple[bool, str]:
        """Collect all inputs from form data and validate required fields"""
        # Clear previous input values
        self.inputs = {}
        self.outputs = {}

        for field in self.config.input_fields:
            input_value = self._get_input(field)

            if not input_value and field in self.config.required_fields:
                return False, field

            if field.startswith("output_"):
                self.outputs[field] = self._get_all_fields_with_defaults(field)
            else:
                self.inputs[field] = input_value

        return True, ""

    def format_command(self) -> str:
        """Format command string with input values"""
        # Use the all_fields property to combine inputs and outputs
        return self.config.command.format(**self.all_fields)

    def get_default_output_file(self) -> Path:
        """Generate a default output file path with timestamp"""

        cwd = Path().cwd().absolute()

        tab = self.config.command.split()[0].lower()
        tool = self.config.name.lower().replace(" ", "_")
        ext = self.config.default_output_ext
        date_time = datetime.now().strftime("%H%M_%d%m%Y")

        file = f"{tool}_{date_time}{ext}"

        if self.config.name == "curl":
            file = (
                self.app.query_one("#curl_url_input", Input)
                .value
                .strip()
            ).split("/")[-1]

        # Create directories if they don't exist
        output_dir = cwd.joinpath("results", tab)
        output_dir.mkdir(exist_ok=True, parents=True)

        return output_dir.joinpath(file)

    def run(self):
        """Main entry point to run the process"""
        success, field = self.validate_inputs()
        if not success:
            self.app.notify(
                f"Please provide a value for [b][i]{field}[/i][/b]",
                title=self.config.name,
                severity="warning"
            )
            return

        self.app.notify(f"Running {self.config.name}...")
        logging.info(f"Running {self.config.name}...")
        self.app.query_one(f"#{self.config.name}_loading").add_class("running")

        try:
            command = self.format_command()
            # For debugging
            self.app.notify(command, title=self.config.name)

            # Start process thread
            thread = threading.Thread(target=self._run_process, args=(command,))
            thread.daemon = True
            thread.start()
        except KeyError as e:
            self.app.notify(
                f"Error formatting command: Missing field [b][i]{e}[/i][/b]",
                title=self.config.name,
                severity="error"
            )
            logging.error(f"Command format error in {self.config.name}: {e}")
            return

    def _run_process(self, command: str):
        """Execute the actual process in a thread"""
        try:
            logging.info(f"Running command: {command}")

            # Ensure results directory exists
            results_dir = Path("results")
            results_dir.mkdir(exist_ok=True)

            # Get executable and arguments
            cmd_parts = command.split()
            executable = cmd_parts[0]

            # Check if executable exists in PATH
            # from shutil import which
            # if which(executable) is None:
            #     self.app.notify(
            #         f"Executable '{executable}' not found in PATH",
            #         title=self.config.display_name,
            #         severity="error",
            #     )

            result = subprocess.run(
                cmd_parts,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            msg = (
                self.config.success_message
                or f"{self.config.name} completed successfully"
            )
            logging.info(msg)
            logging.info(f"Output: {result.stdout}")
            self.app.notify(msg, title=self.config.name)

        except FileNotFoundError as e:
            error_msg = f"Command not found: {command.split()[0]}"
            logging.error(error_msg)
            self.app.notify(
                error_msg,
                title=self.config.name,
                severity="error"
            )

        except subprocess.CalledProcessError as e:
            error_msg = (
                self.config.error_message
                or f"Error in {self.config.name}: {e.stderr}"
            )
            logging.error(error_msg)
            self.app.notify(
                f"An error occurred: {e.stderr[:100]}{'...' if len(e.stderr) > 100 else ''}",
                title=self.config.name,
                severity="error"
            )

        finally:
            self.app.query_one(f"#{self.config.name}_loading").remove_class("running")

