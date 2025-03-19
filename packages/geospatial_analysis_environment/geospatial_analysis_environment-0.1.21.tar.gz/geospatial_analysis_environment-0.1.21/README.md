# Spatial Analysis Environment

This repo abstracts the basics of a spatial analysis environment, so it can be used consistently across microservices.

A slightly weird thing right now:
- We want to use conda for installation, because it helps manage a lot of the dependencies (GDAL)
- But we can't use conda for publishing, because the path to get on conda-forge seems like a pain and we haven't prioritized it. Eventually we'll use pixi, but pixi build is still in development.
- So we're using `uv` to publish, and that introduces some dependency mismatches.  We can see what those are with the `create-mismatch-report` target.  So far they have been minor.  We don't use this report for anything, but it's a useful sanity check.  Keep in mind this is just a mismatch between the base environment in `conda` and `uv`.  Downstream environments pip install base via conda, so there are no mismatches between analysis services (ie `jupyter` and `dask`)
- Eventually we'll switch to conda publishing, probably via `pixi`

## Environments

The `environments` directory contains the base environment and any other environments that are needed.

The `base` environment is the core dependencies for all later tooling and environments.

The `analysis` environment is used for later tooling that is specific to analysis (like RasterOps and VectorOps).

The `jupyter` environment is used for the Jupyter notebook and includes RasterOps and VectorOps.

The `pmtiles` environment is used for the PMTiles tooling.

## Publishing Base Environment

### Adding a new dependency

When adding a new dependency to the project:

1. Add the package to `environments/base/base.yml`:
```yaml
dependencies:
  - new-package>=1.0.0
```

2. Add the same package to `pyproject.toml`:
```toml
dependencies = [
    "new-package>=1.0.0",
]
```

### Publishing the base environment to PyPI

3. Build the base environment:
```bash
make base-build
make base-run
```

4. Update the lock files, within the running container:
```bash
make lock
```
This also generates a mismatch report at `version_info/mismatch_report.txt` to ensure version alignment between conda and uv.

5. Review the mismatch report at `version_info/mismatch_report.txt` to ensure version alignment between conda and uv:

6. Test the environment:
You will need a PyPI token to publish, in `.env.publish`.  Ask someone who has it.
```bash
make publish
```

This publishes the base environment to PyPI, so it can be used in downstream repos (`rasterops`, `vectorops`, etc).

## Building downstream environments
To keep things consistent, we use the base environment to build downstream environments.  It gets `pip` installed via `conda` to ensure compatibility with the base environment.  Downstream environments also need to include the same version of `gdal`, installed via `conda`.  

### Example rasterops environment
```yaml
name: rasterops
channels:
  - conda-forge
dependencies:
  - python>=3.12.0,<3.13.0
  - gdal>=3.10.0
  - pip:
    - geospatial-analysis-environment>=0.1.9
    - coastal_resilience_utilities>=0.1.35
```

## Building the analysis environment

1. Update any dependencies in `environments/analysis/analysis.yml`

2. Build the analysis environment:
```bash
make analysis-build
make analysis-run
```

## Building the jupyter environment

1. Update any dependencies in `environments/jupyter/jupyter.yml`

2. Build the jupyter environment:
```bash
make jupyter-build
make jupyter-run
```


## Prerequisites

1. Install `helm` (On MacOSX):
```bash
brew install helm
```
See https://helm.sh/docs/intro/install/ for other systems.

2. Configure AWS credentials:
Create a file named `.env.s3` with your Nautilus Cept S3 credentials:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_ENDPOINT_URL=your_endpoint_url
```

## Deployment

Create a deployment with a pod, ingress, and persistent volume unique to you:
```bash
make jupyter-push
make jupyter-deploy
```

Release resources when you're done:
```bash
make jupyter-teardown
```

## Developing Dependencies on a deployed Jupyter server

You will need to have `fswatch` installed (`brew install fswatch`). To develop
`rasterops` just run:

```
make dev-rasterops
```

Once we have `vectorops` as a dependency it will be possible to also run:

```
make dev-vectorops
```

If it's common to develop both at the same time let me know and we can pretty
easily add that.

Both of these commands will ensure that there is a server running at
`https://dev-jupyter.nrp-nautilus.io`.

Don't forget to use `importlib` to reload dependencies from disk:

```
import importlib
import rasterops

# If you change a file locally, wait for it to be synced and then run:

importlib.reload(rasterops)

```

If you want to make sure that the dev server is shut down you can just run

```
helm uninstall dev
```
