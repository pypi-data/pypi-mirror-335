# OQC QCaaS Client

The OQC QCaaS Client is our python library serving as the primary interface for the OQC QCaaS service. It provides the capability to submit and manage tasks on our quantum computers and simulators.

For information on how to install and use the Client visit our [documentation](https://docs.oqc.app/).

Note, client versions prior to 3.9.1 are no longer installable because of a yanked dependency. Customers are advised to upgrade to version 3.9.1 or later

## Contributing

Developers should refer to the [qcaas-devstack README](https://github.com/oqc-tech/qcaas-devstack/blob/main/README.md) and follow the instructions there-in to set up the complete QCaaS local development environment.

### Task Runner (`poe`)

> [!NOTE]
> In contrast to the other QCaaS repos, vscode tasks are _**NOT**_ used as the
> default task runner for development tasks (e.g. updating packages, linting).
> Instead, the team is trialing [`poe`](https://poethepoet.natn.io/).

Tasks are defined in the `[tool.poe.tasks]` section of [pyproject.toml](pyproject.toml). The [GitHub workflow used to build](.github/workflows/build.yml) the project uses these same tasks.

Simply type `poe` in an activated virtual environment or Poetry shell to see a 
list of available tasks. To run one of the predefined tasks use the command
`poe {{ TASK_NAME }}`.

Any failures exit with a non-zero exit code and will be immediately obvious:

```bash
Poe => ruff check
qcaas_client/client.py:3:8: F401 [*] `json` imported but unused
...
Found 5 errors.
[*] 1 fixable with the `--fix` option.
Error: Sequence aborted after failed subtask 'lint'
```

> [!TIP]
> To run all checks that should pass prior to PR submission use the command `poe checks`.

```bash
$ poe checks
Poe => poetry check --lock
All set!
Poe => bandit -c bandit_config.yaml -r .
[main]  INFO    Found project level .bandit file: ./.bandit
[main]  INFO    Using command line arg for config file
...
Files skipped (0):
Poe => pip-audit --desc --ignore-vuln GHSA-84pr-m4jr-85g5
No known vulnerabilities found
Poe => ruff check
All checks passed!
Poe => ruff format --check
19 files already formatted
Poe => pip-licenses --fail-on 'GNU General Public License (GPL);GNU Library or Lesser General Public License'
 Name                     Version    License                              
... 
Poe => pytest -v tests/client/unit/
======================= test session starts =======================
platform linux -- Python 3.10.16, pytest-8.3.4, pluggy-1.5.0 -- /home/node/.cache/pypoetry/virtualenvs/oqc-qcaas-client-0Bi17TEg-py3.10/bin/python
...
tests/client/unit/test_version.py::test_qcaas_client_has_version_attribute PASSED [100%]

======================= 24 passed in 0.47s ========================
oqc-qcaas-client-py3.10node@ff06cf96ca22:/qcaas-client$ 
```
