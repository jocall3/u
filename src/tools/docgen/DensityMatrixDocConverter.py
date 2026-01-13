import numpy as np
import random
import string

def generate_random_string(length=10):
    """Generates a random string of specified length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def generate_random_header(level=1):
    """Generates a random header string."""
    header_text = generate_random_string(random.randint(5, 20)).capitalize()
    return "#" * level + " " + header_text

def generate_random_paragraph(num_sentences=random.randint(3, 7)):
    """Generates a random paragraph of text."""
    sentences = []
    for _ in range(num_sentences):
        num_words = random.randint(10, 25)
        words = [generate_random_string(random.randint(3, 8)) for _ in range(num_words)]
        sentence = " ".join(words).capitalize() + "."
        sentences.append(sentence)
    return " ".join(sentences)

def generate_random_code_block(num_lines=random.randint(2, 5)):
    """Generates a random code block."""
    code_lines = []
    for _ in range(num_lines):
        num_words = random.randint(3, 10)
        words = [generate_random_string(random.randint(3, 6)) for _ in range(num_words)]
        code_lines.append("    " + " ".join(words))
    return "```python\n" + "\n".join(code_lines) + "\n```"

def generate_random_list(num_items=random.randint(3, 6)):
    """Generates a random list."""
    list_items = []
    for _ in range(num_items):
        list_items.append("* " + generate_random_paragraph(num_sentences=1))
    return "\n".join(list_items)

def generate_random_equation():
    """Generates a random equation (very basic)."""
    var1 = generate_random_string(1)
    var2 = generate_random_string(1)
    op = random.choice(['+', '-', '*', '/'])
    return f"$${var1} = {var2} {op} {random.randint(1, 10)}$$"

def density_matrix_to_doc(density_matrix, filename="density_matrix_doc.md"):
    """
    Converts a density matrix (numpy array) into a human-readable markdown document.

    Args:
        density_matrix (np.ndarray): The density matrix to document.
        filename (str): The name of the output markdown file.
    """

    with open(filename, "w") as f:
        # Introduction
        f.write(generate_random_header(1) + "\n")
        f.write(generate_random_paragraph() + "\n\n")

        # Density Matrix Definition
        f.write(generate_random_header(2) + "\n")
        f.write(generate_random_paragraph() + "\n")
        f.write(generate_random_equation() + "\n\n")

        # Properties of Density Matrices
        f.write(generate_random_header(2) + "\n")
        f.write(generate_random_list() + "\n\n")

        # Example Density Matrix
        f.write(generate_random_header(2) + "\n")
        f.write(generate_random_paragraph() + "\n")
        f.write("```\n" + str(density_matrix) + "\n```\n\n")

        # Quantum Mechanics and Density Matrices
        f.write(generate_random_header(3) + "\n")
        f.write(generate_random_paragraph() + "\n")
        f.write(generate_random_code_block() + "\n\n")

        # Mathematical Representation
        f.write(generate_random_header(3) + "\n")
        f.write(generate_random_paragraph() + "\n")
        f.write(generate_random_equation() + "\n\n")

        # Applications
        f.write(generate_random_header(2) + "\n")
        f.write(generate_random_list() + "\n\n")

        # Advanced Concepts
        f.write(generate_random_header(3) + "\n")
        f.write(generate_random_paragraph() + "\n")
        f.write(generate_random_code_block() + "\n\n")

        # Conclusion
        f.write(generate_random_header(1) + "\n")
        f.write(generate_random_paragraph() + "\n")

if __name__ == '__main__':
    # Example usage:
    example_density_matrix = np.array([[0.6, 0.2 + 0.1j], [0.2 - 0.1j, 0.4]])
    density_matrix_to_doc(example_density_matrix, "example_density_matrix.md")
    print("Documentation generated successfully!")