import typer

# import boto3
import cloud_base_cli.libs.gitlab as gitlab_lib
import cloud_base_cli.libs.aws as aws
# import gitlab
# import cloud_base_cli.libs.aws as aws
# import lazy_import
# aws = lazy_import.lazy_module("cloud_base_cli.libs.aws")
# gitlab = lazy_import.lazy_module("cloud_base_cli.libs.gitlab")


app = typer.Typer()


@app.callback()
def callback():
    """
    Cloud Base CLI
    """
    pass


@app.command()
def multi(parent_group_id: str):
    """
    Create a new Gitlab Project for multi-account Cloud Runway
    provide parent_group_id
    """
    a = aws.AWS()
    gitlab_lib.set_vars(a.get_secret())
    gitlab_lib.implement(parent_group_id)


@app.command()
def single(parent_group_id: int):
    """
    Create a new Gitlab Project for single account Cloud Runway
    provide parent_group_id
    """
    a = aws.AWS()
    gitlab_lib.set_vars(a.get_secret())
    project_name = "cloud-runway-single"
    gitlab_lib.implement_single(project_name, parent_group_id)


@app.command()
def create_project(project_name: str, parent_group_id: int, project_template_id: int):
    """
    Create a new Gitlab Project from a template
    provide project_name, parent_group_id, project_template_id
    """
    a = aws.AWS()
    gitlab_lib.set_vars(a.get_secret())
    gitlab_lib.create_project_from_template(
        project_name, parent_group_id, project_template_id
    )


@app.command()
def hello(name):
    print(f"hello there {name}")


@app.command()
def version():
    """
    Print the version of the Cloud Base CLI
    """
    import importlib.metadata

    try:
        version = importlib.metadata.version("cloud-base-cli")
        print(f"Cloud Base CLI version: {version}")
    except importlib.metadata.PackageNotFoundError:
        print("Unable to find version information")
