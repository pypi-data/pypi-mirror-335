import marimo

__generated_with = "0.11.13"
app = marimo.App()


@app.cell
def _():
    from oe_python_template_example import Service

    service = Service()
    message = service.get_hello_world()
    print(message)
    return Service, message, service


if __name__ == "__main__":
    app.run()
