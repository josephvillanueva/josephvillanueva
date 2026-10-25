# CircleCI run policy

Feature branches build only with an open pull request, and newer commits cancel outdated branch workflows (provider settings).

Full checks run for pull requests. The default branch does not repeat the same work after merge; direct pushes require local verification first.

Set the `force_full` pipeline parameter to `true` to request a complete manual run, including on the default branch.

This documentation or governed repository retains every existing validator for all changed files, including Markdown.

Original test commands, assertions, machine sizes and security boundaries are retained. No billing, credentials, fork permissions or production data settings are changed.

## Previous setup notes

The run policy above supersedes trigger descriptions in these retained notes.

# Documentation validation

CircleCI runs a small Python job for this documentation repository. It checks
tracked Markdown for empty documents, skipped heading levels, unclosed code
fences and conflict markers. It checks Markdown and HTML relative file links
(including images) for existing targets inside this repository, and parses all
tracked YAML while rejecting duplicate keys.

External URLs and fragment anchors are not checked. The job needs no secrets,
contexts, deployment access, application build or paid services.

To run the same checks locally with Python 3.9 or newer:

```sh
python -m pip install -r .circleci/requirements.txt
python .circleci/validate_docs.py
```

Validate the pipeline separately with the official CircleCI CLI:

```sh
circleci config validate .circleci/config.yml
```

The repository owner must activate the project in CircleCI before hosted runs
can execute.
