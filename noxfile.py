import nox


@nox.session
def tests(session):
    session.install("-r", "requirements.txt")
    session.install("-e", ".")
    session.run("pytest")
