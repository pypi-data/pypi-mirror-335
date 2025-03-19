# cloud-base-cli

Cloud Base CLI App for LZ

# Usage

* Install `pip install cloud-base-cli --upgrade`
* Use Cloud-App-Prod credentials: AWS SSO  needed to get secrets
* Create a new Cloud Base Repo with `cloud-base-cli multi project_name parent_group_id`
    - `parent_group_id` is the company group ID, e.g., https://gitlab.com/groups/stratpoint/atc/-/edit Group ID: 308
* Example:
    - `cloud-base-cli single 308` for single account
    - `cloud-base-cli multi 308` fow multi account
* For help:
    - `cloud-base-cli --help`
    - `cloud-base-cli single --help`



## Requirements

* Python 3.10 or greater.
* Pipx (install [instructions](https://pipx.pypa.io/stable/installation)).

## Installation

* Install `poetry` using `pipx install poetry`.

## Getting started to develop

After template created following steps gets you ups and running with the working cli app.

* Create a virtual enviroment with `python3 -m venv venv` and active it using `source venv/bin/activate`
* Go to project directory and run `pip install -r requirements.txt`
* run `poetry install`
* Run `pre-commit install` to install git hooks.
* Run `cloud-base-cli --help`  run cli.
* Run tests with `pytest`


## Architecture Diagram

![Architecture](cloud-base-cli.drawio.png)
