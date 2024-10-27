# Issues

For this small parsing, we want to get all issues from workload manager repositories, and possibly with this dataset we can do analysis to determine features that are asked for (but not able to be provided) and those that are. Arguably we could do this manually, or just compare to Kubernetes Job in [manual](../manual).

## Usage

Install dependencies to an environment. Note this is in the root.

```bash
cd ../
python -m venv env
source env/bin/activate
pip install -r requirements.txt 
```

Run the script to download issues for workload manager repos.

```bash
python scripts/get_issues.py
```

That will dump issues into [data](data). Note that we can't get SLURM from GitHub because they have some old school issue board that we would need to scrape. I can do this if we decide the data is worth it. Also note that htcondor seems to have issues that reference an old website, so that would need another layer of parsing. I'm not sure I can easily access without an account.
