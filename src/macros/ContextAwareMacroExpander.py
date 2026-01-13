import random
import hashlib

class ContextAwareMacroExpander:
    """
    A class that expands macros based on the runtime context.
    This allows for dynamic code generation and customization.
    """

    def __init__(self, context=None):
        """
        Initializes the ContextAwareMacroExpander with an optional context.

        Args:
            context (dict, optional): A dictionary containing context variables. Defaults to None.
        """
        self.context = context if context is not None else {}
        self.random_seed = random.randint(0, 1000)  # Initialize with a random seed
        random.seed(self.random_seed) # Seed the random number generator

    def set_context(self, context):
        """
        Sets the context for macro expansion.

        Args:
            context (dict): A dictionary containing context variables.
        """
        self.context = context
        self.random_seed = self._hash_context(context) # Update seed based on context
        random.seed(self.random_seed)

    def _hash_context(self, context):
        """
        Hashes the context dictionary to generate a seed.

        Args:
            context (dict): The context dictionary.

        Returns:
            int: A seed value derived from the context.
        """
        context_string = str(context).encode('utf-8')
        hash_object = hashlib.sha256(context_string)
        hex_dig = hash_object.hexdigest()
        return int(hex_dig, 16) % (10 ** 8) # Limit to a reasonable seed size

    def expand_macro(self, macro_string):
        """
        Expands a macro string based on the current context.

        Args:
            macro_string (str): The macro string to expand.

        Returns:
            str: The expanded macro string.
        """
        try:
            # Replace context variables in the macro string
            expanded_string = macro_string.format(**self.context)

            # Add some randomness based on the context and random seed
            random_value = random.random()
            expanded_string += f"_{random_value:.4f}"

            return expanded_string
        except KeyError as e:
            print(f"Error: Missing context variable: {e}")
            return macro_string  # Return the original string if a variable is missing
        except Exception as e:
            print(f"Error during macro expansion: {e}")
            return macro_string

    def generate_random_code_snippet(self, code_type="python", length=10):
        """
        Generates a random code snippet of a specified type and length.

        Args:
            code_type (str, optional): The type of code to generate (e.g., "python", "javascript"). Defaults to "python".
            length (int, optional): The length of the code snippet (number of lines). Defaults to 10.

        Returns:
            str: A random code snippet.
        """
        if code_type == "python":
            lines = [f"print(random.randint(1, 100))  # Line {i+1}" for i in range(length)]
        elif code_type == "javascript":
            lines = [f"console.log(Math.random()); // Line {i+1}" for i in range(length)]
        else:
            lines = [f"// Random line {i+1}" for i in range(length)]

        return "\n".join(lines)

    def generate_dynamic_content(self, template, data):
        """
        Generates dynamic content based on a template and data.

        Args:
            template (str): The template string.
            data (dict): The data to populate the template.

        Returns:
            str: The generated content.
        """
        try:
            return template.format(**data)
        except KeyError as e:
            print(f"Error: Missing data key: {e}")
            return template
        except Exception as e:
            print(f"Error generating dynamic content: {e}")
            return template

if __name__ == '__main__':
    # Example usage
    expander = ContextAwareMacroExpander()

    # Set the context
    context = {"name": "Alice", "age": 30, "city": "New York"}
    expander.set_context(context)

    # Expand a macro string
    macro_string = "Hello, {name}! You are {age} years old and live in {city}."
    expanded_string = expander.expand_macro(macro_string)
    print(f"Expanded string: {expanded_string}")

    # Generate a random code snippet
    code_snippet = expander.generate_random_code_snippet(code_type="python", length=5)
    print(f"\nRandom code snippet:\n{code_snippet}")

    # Generate dynamic content
    template = "The value of x is {x} and the value of y is {y}."
    data = {"x": 10, "y": 20}
    dynamic_content = expander.generate_dynamic_content(template, data)
    print(f"\nDynamic content: {dynamic_content}")

    # Demonstrate context change and its effect
    new_context = {"name": "Bob", "age": 25, "city": "London"}
    expander.set_context(new_context)
    new_expanded_string = expander.expand_macro(macro_string)
    print(f"\nExpanded string with new context: {new_expanded_string}")