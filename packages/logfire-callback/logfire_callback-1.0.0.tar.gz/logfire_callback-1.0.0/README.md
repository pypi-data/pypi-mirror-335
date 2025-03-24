![Plot](https://github.com/louisbrulenaudet/logfire-callback/blob/main/assets/thumbnail.png?raw=true)

# Logfire-callback, observability for Hugging Face's Transformers training loop 🤗
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) ![Maintainer](https://img.shields.io/badge/maintainer-@louisbrulenaudet-blue) ![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg) ![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg) ![Package Manager](https://img.shields.io/badge/package%20manager-uv-purple.svg)

A callback for logging training events from Hugging Face's Transformers to [Logfire](https://logfire.sh) 🤗

## Overview

The `logfire-callback` package provides a seamless integration between Hugging Face's Transformers library and Logfire logging service. It allows you to track and monitor your model training progress, metrics, and events in real-time through Logfire's platform.

## Installation

Install the package using pip:

```bash
pip install logfire-callback
```

## Usage

First, ensure you have a Logfire API token and set it as an environment variable:

```bash
export LOGFIRE_TOKEN=your_logfire_token
```

Then use the callback in your training code:

```python
from transformers import Trainer, TrainingArguments
from logfire_callback import LogfireCallback

# Initialize your model, dataset, etc.

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    # ... other training arguments
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    callbacks=[LogfireCallback()]  # Add the Logfire callback here
)

trainer.train()
```

The callback will automatically log:
- Training start with configuration parameters
- Periodic training metrics (loss, learning rate, etc.)
- Evaluation metrics during validation
- Training completion

## Development

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) for package management

### Setting up the development environment

1. Clone the repository:
```bash
git clone https://github.com/louisbrulenaudet/logfire-callback
cd logfire-callback
```

2. Initialize the development environment:
```bash
make init
```

### Available Make Commands

- `make test` - Run the test suite
- `make check` - Run code quality checks
- `make format` - Format source code
- `make build` - Build the project
- `make upgrade` - Update project dependencies
- `make pre-commit` - Run pre-commit checks

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/louisbrulenaudet/logfire-callback)
- [Issue Tracker](https://github.com/louisbrulenaudet/logfire-callback/issues)

## Requirements

- Python >= 3.11
- transformers >= 4.49.0
- logfire >= 3.9.0

## Citing this project
If you use this code in your research, please use the following BibTeX entry.

```BibTeX
@misc{louisbrulenaudet2025,
	author = {Louis Brulé Naudet},
	title = {Logfire callback, observability for Hugging Face's transformers training loop},
	howpublished = {\url{https://huggingface.co/spaces/louisbrulenaudet/logfire-callback}},
	year = {2025}
}

```
## Feedback
If you have any feedback, please reach out at [louisbrulenaudet@icloud.com](mailto:louisbrulenaudet@icloud.com).
