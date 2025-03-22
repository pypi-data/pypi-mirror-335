from invoke import task


@task
def develop(c):
    c.run("maturin develop --uv")

@task
def example(c, name: str):
    c.run(f"uv run examples/{name}.py")