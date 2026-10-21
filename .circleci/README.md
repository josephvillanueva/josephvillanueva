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
