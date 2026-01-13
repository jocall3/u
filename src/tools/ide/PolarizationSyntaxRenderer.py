import random
import hashlib

class PolarizationSyntaxRenderer:
    """
    Dynamically colors syntax based on simulated photon polarization.

    This class provides a method to render syntax with colors determined by
    simulated photon polarization.  It uses a hashing function to ensure
    consistent color assignments for the same syntax element, while introducing
    randomness to create a visually diverse and engaging experience.
    """

    def __init__(self, seed=None):
        """
        Initializes the PolarizationSyntaxRenderer with an optional seed.

        Args:
            seed (int, optional): A seed for the random number generator.
                                  If None, the system time is used.
        """
        if seed is None:
            self.seed = random.randint(0, 2**32 - 1)  # Use a large range for randomness
        else:
            self.seed = seed
        self.random = random.Random(self.seed)

    def _hash_syntax(self, syntax_element):
        """
        Hashes a syntax element to generate a consistent numerical value.

        Args:
            syntax_element (str): The syntax element to hash.

        Returns:
            int: A numerical hash value.
        """
        hasher = hashlib.sha256()
        hasher.update(syntax_element.encode('utf-8'))
        return int(hasher.hexdigest(), 16)

    def _simulate_photon_polarization(self, hash_value):
        """
        Simulates photon polarization based on the hash value.

        This method uses the hash value to generate a pseudo-random angle
        representing the polarization angle of a photon.  This angle is then
        used to determine the color of the syntax element.

        Args:
            hash_value (int): The hash value of the syntax element.

        Returns:
            tuple: An RGB tuple representing the color.
        """
        # Use the hash value to seed a local random number generator
        local_random = random.Random(hash_value)

        # Generate a pseudo-random polarization angle (0 to 360 degrees)
        polarization_angle = local_random.random() * 360

        # Convert the angle to an RGB color
        # This is a simplified example; more sophisticated color mappings
        # could be used.
        red = int((abs(hash_value % 255) + polarization_angle) % 256)
        green = int((abs(hash_value % 128) + polarization_angle * 2) % 256)
        blue = int((abs(hash_value % 64) + polarization_angle * 3) % 256)

        return (red, green, blue)

    def render_syntax(self, syntax_element):
        """
        Renders a syntax element with a color based on simulated polarization.

        Args:
            syntax_element (str): The syntax element to render.

        Returns:
            str: The syntax element with an inline style attribute containing the color.
        """
        hash_value = self._hash_syntax(syntax_element)
        color = self._simulate_photon_polarization(hash_value)
        return f'<span style="color: rgb({color[0]}, {color[1]}, {color[2]})">{syntax_element}</span>'

    def render_syntax_with_classes(self, syntax_element, base_class="polarized-syntax"):
        """
        Renders a syntax element with a CSS class based on simulated polarization.

        Args:
            syntax_element (str): The syntax element to render.
            base_class (str): The base CSS class to use.

        Returns:
            str: The syntax element with a CSS class attribute containing the color.
        """
        hash_value = self._hash_syntax(syntax_element)
        color = self._simulate_photon_polarization(hash_value)
        color_class = f"{base_class}-{color[0]}-{color[1]}-{color[2]}"
        return f'<span class="{color_class}">{syntax_element}</span>'

if __name__ == '__main__':
    renderer = PolarizationSyntaxRenderer(seed=42)  # Example usage with a seed

    code_snippet = """
    def hello_world():
        print("Hello, world!")
    """

    rendered_code = ""
    for line in code_snippet.splitlines():
        rendered_code += renderer.render_syntax(line) + "\n"

    print(rendered_code)

    # Example using CSS classes
    renderer_css = PolarizationSyntaxRenderer(seed=123)
    css_code_snippet = """
    .my-class {
        color: blue;
        font-size: 16px;
    }
    """
    rendered_css_code = ""
    for line in css_code_snippet.splitlines():
        rendered_css_code += renderer_css.render_syntax_with_classes(line, base_class="css-polarized") + "\n"

    print(rendered_css_code)