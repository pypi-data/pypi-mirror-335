# Cloud SQL Instance Manager

A command-line tool for managing GCP cloud_sql_proxy connections to a number of instances.
It can automatically import your GCP project's Cloud SQL instances, assign ports to them, and start and stop the proxies.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install cloud_sql_instance_manager.

```bash
pip install cloud_sql_instance_manager
```

You will need to have [gcloud command line](https://cloud.google.com/sdk/gcloud) installed and logged in with `gcloud auth login`

The manager will default to using the output of `which cloud_sql_proxy` to determine the location of the cloud_sql_proxy executable. You can override this with

```bash
cloud_sql config --path /FULL/PATH/TO/EXECUTABLE
```

## Usage

### Importing from gcloud

Ensure you are authenticated with gcloud command line.

```bash
cloud_sql import
```

The instance manager will import any (new) instances and automatically assign them ports.

If you want to specify a different project to your current default, then

```bash
cloud_sql import --project YOUR-PROJECT-NAME
```

If you want to remove any old instances that are not found in your cloud project, add the --tidy flag.

```base
cloud_sql import --project YOUR-PROJECT-NAME --tidy
```

### Nicknames

By default, instances are given a nickname of everything proceeding "-instance-" in the full name. For example - `test-application-instance-9956326571963535019` will get the nickname `test-application`
You can amend the nickname with

```bash
cloud_sql update ORIGINAL-NICKNAME --nick NEW-NICKNAME
```

At any point, you can have more than one instance with the same nickname but different projects, and you can differentiate with `--project PROJECT-NAME`

### IAM

Set whether the manager will start the proxy with `--enable_iam_login`

```bash
cloud_sql update NICKNAME --iam true
```

### Starting an instance

```bash
cloud_sql start NICK-NAME
```

### Starting all default instances

```bash
cloud_sql start default
```

Add `--project YOUR-PROJECT` to start only default instances for a particular project

### Stopping an instance

```bash
cloud_sql stop NICK-NAME
```

### Stopping all running instances

```bash
cloud_sql stop all
```

### Listing instances

List all instances

```bash
cloud_sql list
```

List all instances for a project

```bash
cloud_sql list --project YOUR-PROJECT
```

List all running instances

```bash
cloud_sql list-running
```

## Tests

To run with coverage

```bash
pip install coverage
coverage run -m pytest
```

## Releasing

Install `build` and `twine`.

```bash
pip install twine build
```

Build with

```bash
python -m build
```

Release to test with

```bash
twine upload -r testpypi dist/*
```

Release to live with

```bash
twine upload -r pypi dist/*
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## TODO List

- Export to DBeaver
- Use nickname or name interchangeably
