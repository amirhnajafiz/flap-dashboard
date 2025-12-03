from flask import render_template


def index():
    """
    Render the index.html file.
    :return: The rendered index.html file.
    """
    return render_template("index.html")
