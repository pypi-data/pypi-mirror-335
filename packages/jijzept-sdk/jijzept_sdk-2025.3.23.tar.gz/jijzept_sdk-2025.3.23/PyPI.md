# JijZeptSDK

JijZeptSDK is a package that allows you to install all the free packages provided by JijZept. Specifically, it includes the following Python packages.

- [jijmodeling](https://pypi.org/project/jijmodeling/)
- [ommx](https://pypi.org/project/ommx/)
- [ommx-python-mip-adapter](https://pypi.org/project/ommx-python-mip-adapter/)
- [ommx-pyscipopt-adapter](https://pypi.org/project/ommx-pyscipopt-adapter/)
- [ommx-highs-adapter](https://pypi.org/project/ommx-highs-adapter/)
- [ommx-fixstars-amplify-adapter](https://pypi.org/project/ommx-fixstars-amplify-adapter/)
- [ommx-gurobipy-adapter](https://pypi.org/project/ommx-gurobipy-adapter/)
- [ommx-openjij-adapter](https://pypi.org/project/ommx-openjij-adapter/)
- [minto](https://pypi.org/project/minto/)
- [qamomile](https://pypi.org/project/qamomile/)

## Basic usage

The following command allows you to install the free packages provided by JijZept along with `jupyterlab`.

```bash
pip install "jijzept_sdk[all]"
```

You can also start the JupyterLab environment with the following command.

```bash
jijzept_sdk
```

## Advanced usage

You can also install only some packages by specifying options like the following command. However, `jijmodeling` and `ommx` are always included.

```bash
pip install “jijzept_sdk[mip]"
```

The list of options is as follows:

- `mip`: Install packages for using `ommx-python-mip-adapter`.
- `scip`: Install packages for using `ommx-pyscipopt-adapter`.
- `highs`: Install packages for using `ommx-highs-adapter`.
- `amplify`: Install packages for using `ommx-fixstars-amplify-adapter`.
- `gurobi`: Install packages for using `ommx-gurobipy-adapter`.
- `openjij`: Install packages for using `ommx-openjij-adapter`.
- `qamomile`: Install packages for using `qamomile`.
- `minto`: Install packages for using `minto`.
- `lab`: Install packages for using `jupyterlab`.

Note that the `lab` option is required to run the `jijzept_sdk` command.
