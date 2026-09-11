from edtrace import text, image, note


def main():
    text("# Lecture 1: introduction")

    x = 3  # @inspect x
    text("Start from a single number.")

    x = square(x)  # @inspect x

    image("images/pipeline.png", width=600)
    note("Ask the class to predict the output before stepping forward.")

    prepare_dataset()  # @stepover


def square(value: int) -> int:
    return value * value  # @inspect value


def prepare_dataset():
    """Long, uninteresting setup."""
    return list(range(1000))
