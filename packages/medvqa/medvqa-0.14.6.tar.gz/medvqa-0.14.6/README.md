---
sdk: gradio
sdk_version: 4.44.1
app_file: gradio_interface.py
---
# MedVQA

A CLI tool for MedVQA competition (https://github.com/simula/ImageCLEFmed-MEDVQA-GI-2025).

## Installation

```bash
pip install -U medvqa
```
The library is under heavy development. So, we recommend to always make sure you have the latest version installed.

## Usage

```bash
medvqa validate_and_submit --competition=gi-2025 --task=1 --repo_id=...
```
where repo_id is your HuggingFace Model repo id (like SushantGautam/XXModelCheckpoint) submission script, for eg, submission_task1.py file for task 1.

Submission for task 2 is not yet implemented. Will be soon live. Stay tuned.
