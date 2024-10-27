# Kubernetes Job and JobSet

We want to get a set of Kubernetes job.yaml files, with `Kind: Job` (will include JobSet) to understand the kind of workloads that are being run. Since we are very limited with GitHub search, we have to again get around that with an enormous number of terms, and hope we get enough (unique, based on content hashes) results.

## Usage

Install dependencies to an environment. Note this is in the root.

```bash
cd ../
python -m venv env
source env/bin/activate
pip install -r requirements.txt 
```

Run the script to do the search. You'll need to export your GITHUB_TOKEN to the environment.

```bash
export GITHUB_TOKEN=xxxxxxxxxxx
python scripts/search.py
```
