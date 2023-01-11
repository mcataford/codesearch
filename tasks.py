from invoke import task


@task
def lint(ctx):
    ctx.run("black *.py src")
