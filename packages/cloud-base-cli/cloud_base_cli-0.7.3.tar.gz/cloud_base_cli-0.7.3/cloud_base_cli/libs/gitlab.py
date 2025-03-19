# Imports
import os
import git
import gitlab
import shutil
from time import sleep

# Gitlab object
gl = None


def hello():
    print("Hello")


def set_vars(vars):
    global VAR_PROJECT_DEFAULT_TEMPLATE_REPO_ID
    global VAR_PROJECT_DEFAULT_TEMPLATE_DIR
    global VAR_GITLAB_TOKEN
    global VAR_GITLAB_URL
    global VAR_PROJECT_SINGLEACCOUNT_TEMPLATE_REPO_ID
    global gl

    VAR_PROJECT_DEFAULT_TEMPLATE_REPO_ID = vars["VAR_PROJECT_DEFAULT_TEMPLATE_REPO_ID"]
    VAR_PROJECT_SINGLEACCOUNT_TEMPLATE_REPO_ID = vars[
        "VAR_PROJECT_SINGLEACCOUNT_TEMPLATE_REPO_ID"
    ]
    VAR_PROJECT_DEFAULT_TEMPLATE_DIR = vars["VAR_PROJECT_DEFAULT_TEMPLATE_DIR"]
    VAR_GITLAB_TOKEN = vars["VAR_GITLAB_TOKEN"]
    VAR_GITLAB_URL = vars["VAR_GITLAB_URL"]

    gl = gitlab.Gitlab(VAR_GITLAB_URL, private_token=VAR_GITLAB_TOKEN)


def create_project(project_name, project_group_id):
    """
    [Function] Create new project
    """
    project = gl.projects.create(
        {"name": project_name, "namespace_id": project_group_id}
    )

    print(
        f"\t - Project {project_name} with id no. {project.id} was created successfully"
    )

    return project


def create_subgroup(subgroup_name, subgroup_desc, parent_group_id):
    """
    [Function] Create subgroup
    """
    subgroup_details = None
    parent_group = gl.groups.get(parent_group_id)
    subgroup = next(
        (s for s in parent_group.subgroups.list() if s.name == subgroup_name), None
    )

    if subgroup:
        print(f"Subgroup '{subgroup.name}' with ID '{subgroup.id}' already exists.")
        subgroup_details = subgroup
    else:
        new_subgroup = gl.groups.create(
            {
                "name": subgroup_name,
                "path": subgroup_name,
                "description": subgroup_desc,
                "parent_id": parent_group_id,
            }
        )
        subgroup_details = new_subgroup
        print(
            f"New subgroup '{new_subgroup.name}' created with ID '{new_subgroup.id}'."
        )

    return subgroup_details


def clone_project(project_template_id, local_path):
    """
    [Function] Clone existing project
    """
    project = gl.projects.get(project_template_id)
    project_url = project.http_url_to_repo

    protocol, hostname = project_url.split("://")
    credentials = f"gitlab:{VAR_GITLAB_TOKEN}@{hostname}"
    modified_url = f"{protocol}://{credentials}"
    # git@gitlab.stratpoint.cloud:stratpoint/templates/aws/cloud-base-multi-account.git
    # https://gitlab.stratpoint.cloud/stratpoint/templates/aws/cloud-base-multi-account.git
    # https://gitlab:glpat-S3JnTZm-ygmnrvH41N7x@gitlab.stratpoint.cloud/stratpoint/templates/aws/cloud-base-multi-account.git
    repo = git.Repo.clone_from(modified_url, local_path)

    sleep(10)
    print("\t - Template repository cloned successfully")

    return repo


def push_files(project_id, folder_path):
    """
    [Function] Push templates
    """
    commit_actions = []
    project = gl.projects.get(project_id)

    for root, dirs, files in os.walk(folder_path):
        # Skip the .git directory
        if ".git" in dirs:
            dirs.remove(".git")

        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, "rb") as file:
                content = file.read()

            file_path = file_path.replace(folder_path, "", 1)
            action = {
                "action": "create",
                "file_path": file_path,
                "content": content.decode(),
            }
            commit_actions.append(action)

    # Push the changes to the remote repository
    commit = project.commits.create(
        {
            "branch": "main",
            "commit_message": "Initial commit",
            "actions": commit_actions,
        }
    )

    print(f"\t - Commit created with ID: {commit.id}")


def replace_string_in_file(file_path, var_key, var_value):
    """
    [Function] Replace variables
    """
    # Read the file
    with open(file_path, "r") as file:
        file_contents = file.read()

    # Replace the string
    modified_contents = file_contents.replace(var_key, var_value)

    # Write the modified contents to a new file
    with open(file_path, "w") as file:
        file.write(modified_contents)


def replace_filename(directory, old_filename, new_filename):
    """
    [Function] Replace filename
    """
    # Get the full path of the file
    file_path = os.path.join(directory, old_filename)

    # Rename
    new_path = os.path.join(directory, new_filename)
    os.rename(file_path, new_path)
    print(f"\t - File '{old_filename}' renamed to '{new_filename}'")


def delete_directory(directory):
    """
    [Function] Delete a directory
    """
    try:
        shutil.rmtree(directory)
        print(f"\t - Directory '{directory}' deleted successfully.")
    except FileNotFoundError:
        print(f"\t - Directory '{directory}' not found.")
    except Exception as e:
        print(
            f"\t - An error occurred while deleting directory '{directory}': {str(e)}"
        )


def implement(parent_group_id):
    # VAR_PROJECT_COMPANY_NAME = project_name
    VAR_PROJECT_DEFAULT_PARENT_GROUP_ID = parent_group_id
    # Implementation Flow
    try:
        print("Setup starting...")

        project = None
        setup_status = None
        aft_repos = [
            "aft-account-request",
            "aft-global-customizations",
            "aft-account-customizations",
            "aft-account-provisioning-customizations",
        ]

        # project_subgroup = create_subgroup(
        #     VAR_PROJECT_COMPANY_NAME,
        #     "Project Folder",
        #     VAR_PROJECT_DEFAULT_PARENT_GROUP_ID,
        # )

        aft_subgroup = create_subgroup(
            "control-tower",
            "Control Tower Project",
            VAR_PROJECT_DEFAULT_PARENT_GROUP_ID,
        )
        repo = clone_project(
            VAR_PROJECT_DEFAULT_TEMPLATE_REPO_ID, VAR_PROJECT_DEFAULT_TEMPLATE_DIR
        )

        # AFT Default Repos
        for repo in aft_repos:
            print(f"\t - Processing {repo}")

            project = create_project(repo, aft_subgroup.id)
            push_files(project.id, f"{VAR_PROJECT_DEFAULT_TEMPLATE_DIR}/{repo}")

        # AFT Bootstrap Repo
        project = create_project("aft-bootstrap", aft_subgroup.id)
        replace_filename(
            f"{VAR_PROJECT_DEFAULT_TEMPLATE_DIR}/aft-bootstrap",
            ".gitlab-ci.tpl",
            ".gitlab-ci.yml",
        )
        replace_string_in_file(
            f"{VAR_PROJECT_DEFAULT_TEMPLATE_DIR}/aft-bootstrap/backend.tf",
            "$GITLAB_ID",
            str(project.id),
        )
        push_files(project.id, f"{VAR_PROJECT_DEFAULT_TEMPLATE_DIR}/aft-bootstrap")

        # Wait for pipeline to finish
        print("\t - Checking the pipeline")

        # while True:
        #     pipelines = project.pipelines.list()
        #     if any(
        #         pipeline.status in ["success", "cancelled", "failed"]
        #         for pipeline in pipelines
        #     ):
        #         break
        #     print("\t\t -> Waiting for the pipeline to finish...")
        #     sleep(20)

        # # Get the latest pipeline and its status
        # latest_pipeline = project.pipelines.get(pipelines[0].id)
        # pipeline_status = latest_pipeline.status

        # print(f"\t - Pipeline status: {pipeline_status}")
        setup_status = "success"

    except Exception as e:
        print("\t - Error: ", e)

    finally:
        delete_directory(VAR_PROJECT_DEFAULT_TEMPLATE_DIR)

        if setup_status == "success":
            print("Setup finished!")
        else:
            print("Setup aborted!")


def copy_project(project, project_id):
    """
    [Function] Copy Gitlab project from project_id
    """
    try:
        print("Cloning project...")
        folder_path = f"{VAR_PROJECT_DEFAULT_TEMPLATE_DIR}"
        clone_project(project_id, folder_path)
        replace_filename(
            folder_path,
            ".gitlab-ci.tpl",
            ".gitlab-ci.yml",
        )
        replace_string_in_file(
            f"{folder_path}/backend.tf",
            "REPLACE_ME",
            str(project.id),
        )
        commit_actions = []
        # Add all files in the directory to the project
        for root, dirs, files in os.walk(folder_path):
            if ".git" in dirs:
                dirs.remove(".git")
            for file in files:
                if file.endswith((".png", ".jpg")):
                    continue
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder_path)

                try:
                    with open(file_path, "r") as f:
                        file_content = f.read()
                except UnicodeDecodeError:
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                    file_content = file_content.decode(errors="ignore")
                commit_actions.append(
                    {
                        "action": "create",
                        "file_path": relative_path,
                        "content": file_content,
                    }
                )
        project.commits.create(
            {
                "branch": "main",
                "commit_message": "Initial commit from template",
                "actions": commit_actions,
            }
        )
    except Exception as e:
        print("\t - Error Copy Project: ", e)
    finally:
        delete_directory(VAR_PROJECT_DEFAULT_TEMPLATE_DIR)


def implement_single(project_name, parent_group_id):
    # Implementation Flow
    try:
        print("Setup starting...")

        setup_status = None

        print("Creating project...")
        project = create_project(project_name, parent_group_id)
        # Get the project object
        # project = gl.projects.get(883)
        print(
            f"\t - Project {project_name} with id no. {project.id} was created successfully"
        )

        copy_project(project, VAR_PROJECT_SINGLEACCOUNT_TEMPLATE_REPO_ID)        

        setup_status = "success"

    except Exception as e:
        print("\t - Error: ", e)

    finally:

        if setup_status == "success":
            print("Setup finished!")
        else:
            print("Setup aborted!")


def create_project_from_template(project_name, parent_group_id, project_template_id):
    """
    Create a new Gitlab project from a template
    """
    try:
        # Create a new project
        project = create_project(project_name, parent_group_id)
        print(
            f"\t - Project {project_name} with id no. {project.id} was created successfully"
        )
        copy_project(project, project_template_id)

        # Wait for pipeline to finish
        print("\t - Checking the pipeline")
        setup_status = "success"

    except Exception as e:
        print("\t - Error: ", e)
        setup_status = "failed"

    if setup_status == "success":
        print("Setup finished!")
    else:
        print("Setup aborted!")
