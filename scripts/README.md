# Discovery Artifact Automation
Discovery Artifacts are automatically updated using a Github Action script. This
documentation is intended for users that need to maintain the repository.

## Updating discovery artifacts locally

To update discovery artifacts locally:
1. Create a virtual environment using `pyenv virtualenv updateartifacts`
2. Activate the virtual environment using `pyenv activate updateartifacts`
3. Clone the repository, and `cd` into the `scripts` directory
4. Run `pip install -r requirements.txt`
5. Run `pip install -e ../`
6. Run `git checkout -b update-discovery-artifacts-manual`
7. Run `python3 updatediscoveryartifacts.py`
8. Run `./createcommits.sh`
9. Run `python3 buildprbody.py`
10. Create a pull request with the changes.
11. Copy the contents of `temp/allapis.summary` into the PR Body.

## Questions
Feel free to submit an issue!
