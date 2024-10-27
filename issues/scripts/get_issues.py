#!/usr/bin/env python3

import requests
import json
import sys
import os
import time

# Get GitHub issues for popular workload managers.
# We can separate open/closed and (maybe)? find a way to figure out
# what features people want / are asking for, but can't get.

token = os.environ.get("GITHUB_TOKEN")
if not token:
    sys.exit("Please export GITHUB_TOKEN")

headers = {"Authorization": f"token {token}"}

# This is actually the root, here is scripts directory
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_issues(repo):
    """
    Get GitHub issues (open and closed) for a repository.
    The API limit is 5K requests / hour for authenticated.
    If we go over, we sleep an hour.
    """
    url = f"https://api.github.com/repos/{repo}/issues"

    # open, closed, all
    params = {"per_page": 100, "state": "all"}
    issues = []
    while True:
        print(url)
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 403:
            print("Rate limit reached, sleeping one hour")
            time.sleep(3600)
        response.raise_for_status()
        new_issues = response.json()
        if not new_issues:
            break
        issues += new_issues

        # Extract the next page URL from header
        if "next" not in response.links:
            break
        url = response.links["next"]["url"]
        time.sleep(1)

    return issues


# These are workload managers we want to parse
# Note that slurm would need different parsing... ug
# https://support.schedmd.com/
repos = [
    #    "SchedMD/slurm",
    "flux-framework/flux-core",
    "flux-framework/flux-sched",
    "openpbs/openpbs",
    "htcondor/htcondor",
    "adaptivecomputing/torque",
    "IBM-Cloud/hpc-cluster-lsf",
    "volcano-sh/volcano",
    "kubernetes-sigs/kueue",
]


def write_json(obj, path):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(path, "w") as fd:
        fd.write(json.dumps(obj, indent=4))


def read_json(path):
    with open(path, "r") as fd:
        content = json.loads(fd.read())
    return content


def main():
    data_dir = os.path.join(here, "data")

    # Keep track of some basic metrics
    metrics = {}
    metrics_path = os.path.join(data_dir, "metrics.json")
    if os.path.exists(metrics_path):
        metrics = read_json(metrics_path)

    for repo in repos:
        issues_path = os.path.join(data_dir, repo, "issues.json")
        if os.path.exists(issues_path):
            print(f"We already have issues for {repo}")
            continue
        print(f"Getting issues for {repo}")
        issues = get_issues(repo)

        # Really, slurm? Ug.
        if not issues:
            print(f"{repo} does not have issues.")
            continue

        write_json(issues, issues_path)
        counts = {"open": 0, "closed": 0, "total": 0}
        for issue in issues:
            counts[issue["state"]] += 1
            counts["total"] += 1
        metrics[repo] = counts

    # Save metrics to file
    write_json(metrics, metrics_path)


if __name__ == "__main__":
    main()
