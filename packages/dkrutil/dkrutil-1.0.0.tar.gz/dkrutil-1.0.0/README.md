# Dkrutil

Dkrutil is a command-line tool that provides utility functions for managing Docker containers, volumes, and images.
It simplifies common tasks like listing running containers, backing up and restoring volumes, and retrieving Docker
image tags from Docker Hub.

## Installation

You can install dkrutil directly from PyPI:

```bash
pip install dkrutil
```

Or install it using [Poetry](https://python-poetry.org/) for development:

```bash
poetry install
```

## Usage

Dkrutil provides the `dkrutil` command with various subcommands.

### Containers

#### List running containers

```bash
dkrutil containers ps
```

Options:

- `-a, --all` → Show all containers, including stopped ones.

### Volumes

#### Backup Docker volumes

```bash
dkrutil volumes backup -d /path/to/backup
```

Options:

- `-d, --backup-directory` → Directory where the volumes will be backed up.
- `-i, --include` → Regex pattern to include specific volumes (can be repeated).
- `-I, --ignore` → Regex pattern to ignore specific volumes (can be repeated).
- `-v, --verbose` → Show skipped volumes in real time.

#### Restore Docker volumes

```bash
dkrutil volumes restore -d /path/to/backup
```

Options:

- `-d, --backup-directory` → Directory containing the backup files.

### Images

#### Retrieve all tags of an image

```bash
dkrutil images tags alpine
```

Options:

- `-d, --digest` → Filter tags by a specific SHA256 digest.
- `-t, --tag` → Retrieve the digest of a specific tag.

## Configuration

Dkrutil uses the `docker` Python library to interact with the Docker API. Ensure Docker is installed and running
before using this tool.

## Development

Clone the repository:

```bash
git clone https://github.com/emerick-biron/dkrutil.git
cd dkrutil
```

Install dependencies:

```bash
poetry install
```

Run the tool locally:

```bash
poetry run dkrutil --help
```

