import random
import re

class CommandMorpher:
    """
    A class to probabilistically transform CLI commands.

    This class takes a CLI command as input and applies a series of
    transformations based on configurable probabilities. The transformations
    include:

    - Argument addition/removal
    - Option modification
    - Command substitution
    - Syntax alteration
    """

    def __init__(self, config=None):
        """
        Initializes the CommandMorpher with a configuration.

        Args:
            config (dict, optional): A dictionary containing configuration
                                      parameters for the transformations.
                                      Defaults to None, which uses default
                                      probabilities.
        """
        self.config = config or self._default_config()

    def _default_config(self):
        """
        Returns a default configuration dictionary.

        This configuration defines the probabilities for different types of
        transformations.
        """
        return {
            "add_argument_probability": 0.15,
            "remove_argument_probability": 0.10,
            "modify_option_probability": 0.20,
            "command_substitution_probability": 0.05,
            "syntax_alteration_probability": 0.05,
            "argument_pool": ["--verbose", "--debug", "--help", "--version", "-v", "-d", "-h"],
            "command_alternatives": {
                "ls": ["dir", "list"],
                "cat": ["type", "print"],
                "grep": ["find", "search"],
                "rm": ["del", "remove"]
            }
        }

    def morph(self, command):
        """
        Applies probabilistic transformations to the given command.

        Args:
            command (str): The CLI command to transform.

        Returns:
            str: The transformed CLI command.
        """
        command = self._add_argument(command)
        command = self._remove_argument(command)
        command = self._modify_option(command)
        command = self._command_substitution(command)
        command = self._syntax_alteration(command)
        return command

    def _add_argument(self, command):
        """
        Probabilistically adds an argument to the command.
        """
        if random.random() < self.config["add_argument_probability"]:
            argument = random.choice(self.config["argument_pool"])
            command += " " + argument
        return command

    def _remove_argument(self, command):
        """
        Probabilistically removes an argument from the command.
        """
        if random.random() < self.config["remove_argument_probability"]:
            parts = command.split()
            if len(parts) > 1:
                index_to_remove = random.randint(1, len(parts) - 1)  # Don't remove the base command
                del parts[index_to_remove]
                command = " ".join(parts)
        return command

    def _modify_option(self, command):
        """
        Probabilistically modifies an option in the command.
        """
        if random.random() < self.config["modify_option_probability"]:
            parts = command.split()
            for i, part in enumerate(parts):
                if part.startswith("-") and len(part) > 1:  # It's an option
                    if random.random() < 0.5: # Modify the option value
                        if i + 1 < len(parts) and not parts[i+1].startswith("-"):
                            parts[i+1] = str(random.randint(1, 100)) # Replace with a random number
                    else: # Modify the option itself
                        if part in self.config["argument_pool"]:
                            new_option = random.choice(self.config["argument_pool"])
                            parts[i] = new_option
            command = " ".join(parts)
        return command

    def _command_substitution(self, command):
        """
        Probabilistically substitutes the command with an alternative.
        """
        if random.random() < self.config["command_substitution_probability"]:
            parts = command.split()
            base_command = parts[0]
            if base_command in self.config["command_alternatives"]:
                alternatives = self.config["command_alternatives"][base_command]
                new_command = random.choice(alternatives)
                parts[0] = new_command
                command = " ".join(parts)
        return command

    def _syntax_alteration(self, command):
        """
        Probabilistically alters the syntax of the command.
        """
        if random.random() < self.config["syntax_alteration_probability"]:
            # Example: Add extra spaces
            if random.random() < 0.5:
                command = command.replace(" ", "  ")
            else:
                # Example: Change quotes
                if '"' in command:
                    command = command.replace('"', "'")
                elif "'" in command:
                    command = command.replace("'", '"')
        return command

if __name__ == '__main__':
    morpher = CommandMorpher()
    original_command = "ls -l /home"
    morphed_command = morpher.morph(original_command)
    print(f"Original command: {original_command}")
    print(f"Morphed command: {morphed_command}")

    config = {
        "add_argument_probability": 0.8,
        "remove_argument_probability": 0.0,
        "modify_option_probability": 0.0,
        "command_substitution_probability": 0.9,
        "syntax_alteration_probability": 0.0,
        "argument_pool": ["--all", "--recursive"],
        "command_alternatives": {
            "ls": ["dir"]
        }
    }
    morpher2 = CommandMorpher(config)
    morphed_command2 = morpher2.morph(original_command)
    print(f"Morphed command with custom config: {morphed_command2}")