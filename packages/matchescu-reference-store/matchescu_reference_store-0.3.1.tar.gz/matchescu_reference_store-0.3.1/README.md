# Reference Store

The entity reference store's main job is to keep entity references known by the system.
Depending on the entity resolution model being used, it may persist relations between
entity references.

The entity reference store logically organizes the data it stores in workspaces.
Each workspace corresponds to an entity resolution problem domain. For example,
users might have one workspace for resolving publications across multiple data sources
and another workspace for resolving e-commerce products across vendor databases.

# Development

First, ensure that the package builds locally and that the automated test suite runs
fine.

```shell
$ make bootstrap
$ make test
```

Then follow the coding guidelines to submit new contributions.

# Usage

This package is meant to be used as a subsystem in a larger entity resolution pipeline.
The functionalities should be imported and used as per the pipeline's requirements.
