#!/usr/bin/env python3

# We are going to try and search based on terms again

import json
import requests
import logging
import os
import time
import yaml
import sys

logging.basicConfig(level=logging.INFO)

# We want the root
here = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

if "GITHUB_TOKEN" not in os.environ:
    sys.exit("Please export your GITHUB_TOKEN to the environment.")

# do not clone LFS files
os.environ["GIT_LFS_SKIP_SMUDGE"] = "1"
token = os.environ["GITHUB_TOKEN"]
# g = Github(os.environ["GITHUB_TOKEN"])
repos = []


class Stopwatch:
    def __init__(self):
        self.start_time = None
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.start_time = time.perf_counter()
            self.is_running = True

    def stop(self):
        if self.is_running:
            elapsed_time = time.perf_counter() - self.start_time
            self.is_running = False
            return elapsed_time

    def lap(self):
        if self.is_running:
            return time.perf_counter() - self.start_time

    def reset(self):
        self.start_time = None
        self.is_running = False


# We will use this to count minutes for the search api, ug
stopwatch = Stopwatch()


def read_yaml(filename):
    with open(filename, "r") as fd:
        content = yaml.load(fd, Loader=yaml.FullLoader)
    return content


def save_json(results, datapath):
    with open(datapath, "w") as fd:
        fd.write(json.dumps(results))


def save_text(content, path):
    with open(path, "w") as fd:
        fd.write(content)


headers = {"Authorization": f"token {token}"}


hpc_terms = [
    "gpu",
    "gcc",
    "array",
    "module",
    "mpi",
    "roc",
    "cuda",
    "intel",
    "openmpi",
    "mpirun",
    "gcc",
    "clang",
]

app_terms = [
    "gmx",
    "namd",
    "lammps",
    "python",
    "amd",
    "amg",
    "cmake",
    "meson",
    "paraview",
    "hpctoolkit",
    "ninja",
    "rust",
    "spack",
    "easybuild",
    "resnet",
    "pytorch",
    "nvidia",
    "tensorflow",
    "pmix",
    "kripke",
    "quicksilver",
    "maestro",
    "snakemake",
    "nextflow",
    "dask",
    "kubeflow",
    "docker",
    "singularity",
    "valgrind",
    "julia",
    "matlab",
    "nccl",
    "ray",
    "fio",
    "ior",
    "petsc",
    "openfoam",
    "ansys",
    "fftw" "hpl",
    "linpack",
    "stream",
    "adios",
    "adiak",
    "aml",
    "ant",
    "arbor",
    "argo",
    "ascent",
    "auto",
    "bash",
    "bats",
    "bazel",
    "samtools",
    "bison",
    "blt",
    "bolt",
    "boost",
    "bwa",
    "cromwell",
    "cabana",
    "cairo",
    "caliper",
    "camp",
    "chai",
    "chapel",
    "clara",
    "cpuinfo",
    "cromwell",
    "cudnn",
    "nvidia-smi",
    "curl",
    "darshan",
    "data",
    "doxy",
    "elf",
    "dyninst",
    "exa",
    "flex",
    "free",
    "gzip",
    "bench",
    "mark",
    "kokkos",
    "proto",
    "jq",
    "hypre",
    "hpc",
    "hip",
    "hdf5",
    "tree",
    "pack",
    "legion",
    "lbann",
    "archive",
    "less",
    "circle",
    "dwarf",
    "event",
    "proxy",
    "fabric",
    "fuse",
    "crypt",
    "gpg",
    "ice",
    "conv",
    "turbo",
    "svg",
    "access",
    "png",
    "slirp",
    "sodium",
    "ssh",
    "tiff",
    "uring",
    "bpf",
    "term",
    "which",
    "xterm",
    "x11",
    "xc",
    "ext",
    "xml",
    "render",
    "munge",
    "mfem",
    "metis",
    "glu",
    "meson",
    "mercury",
    "magma",
    "m4",
    "lua",
    "perl",
    "lmod",
    "llvm",
    "zmq",
    "lima",
    "nccl",
    "ncurses",
    "nekbone",
    "kueue",
    "operator",
    "npm",
    "node",
    "openblas",
    "opencv",
    "openjdk",
    "java",
    "osu",
    "perl",
    "papi",
    "parallel",
    "pcre",
    "picard",
    "pigz",
    "pmix",
    "pkg",
    "thread",
    "py-",
    "celery",
    "grpc",
    "blue",
    "google",
    "azure",
    "auth",
    "future",
    "fire",
    "exception",
    "hugging",
    "mistral",
    "llm",
    "lazy",
    "kombu",
    "vanessa",
    "jupyter",
    "hub",
    "json",
    "jax",
    "merlin",
    "matplotlib",
    "tune",
    "mpi4py",
    "iter",
    "dict",
    "network",
    "node",
    "graph",
    "numba",
    "openai",
    "retry",
    "rsa",
    "rich",
    "scipy",
    "scikit",
    "learn",
    "sql",
    "sqlite",
    "db",
    "database",
    "cache",
    "toml",
    "tensor",
    "vector",
    "urllib",
    "torch",
    "tornado",
    "cherry",
    "version",
    "virtual",
    "venv",
    "vine",
    "sock",
    "zip",
    "qemu",
    "thread",
    "raja",
    "cpp",
    "readline",
    "grep",
    "csh",
    "rust",
    "ruby",
    "cargo",
    "bootstrap",
    "salmon",
    "sed",
    "awk",
    "squash",
    "strum",
    "super",
    "sun",
    "swig",
    "tar",
    "tex",
    "time",
    "trilinos",
    "unify",
    "umap",
    "cxx",
    "util",
    "valgrind",
    "vtk",
    "z3",
    "zlib",
    "zip",
    "yarn",
]

ml_terms = [
    "tensorboard",
    "scikit",
    "keras",
    "mllib",
    "spark",
    "submit",
    "flux",
    "slurm",
    "sbatch",
    "srun",
    "xgboost",
    "lightgbm",
    "catboost",
    " R ",
    "julia",
    "matlab",
    "octave",
    "gcloud",
    "ai-platform",
    "aws",
    "sagemaker",
    "efa",
    "amazon",
    "scala",
    "git",
    "conda",
    "npm",
    "flask",
    "uvicorn",
    "seaborn",
    "dask",
    "numpy",
    "pandas",
]

terms = set(app_terms + hpc_terms + ml_terms)


def do_search(search_string, save_path):
    """
    Do a search up to 1000 results with specific terms
    """
    results = []

    # We are only allowed 10 requests/hour, ug.
    page = 1
    while True:
        url = f"https://api.github.com/search/code?q={search_string}&per_page=100&page={page}"
        # https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28
        time.sleep(1)
        print(url)
        response = requests.request("GET", url, headers=headers)
        print(response.status_code)
        data = response.json()

        if response.status_code == 403:
            take_a_break()
            continue

        # This will be the same, only announce one page
        if page == 1:
            print(f"  Found {data['total_count']} results")
        if "items" not in data:
            print(data)
        results += data["items"]
        if "next" not in response.links or page == 9:
            break
        page += 1

    # One more save - save 0 so we don't retry it
    zero_marker = f"{save_path}.0"
    if len(results) == 0:
        save_json(results, zero_marker)
    else:
        save_json(results, save_path)


def take_a_break():
    # we only are allowed 10/minute
    global stopwatch
    elapsed_time = stopwatch.stop()

    # Add some wiggle room to sleep until next minute
    sleep_time = 60 - (elapsed_time - 5)
    sleep_time = max(sleep_time, 0)
    print(f"⏱️  Sleeping {sleep_time} seconds")
    stopwatch.reset()
    time.sleep(sleep_time)
    stopwatch.start()


def read_file(path):
    with open(path, "r") as fd:
        content = fd.read()
    return content


def load_json(path):
    return json.loads(read_file(path))


def download(url, path):
    """
    Download a file to a specific path
    """
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "wb") as fd:
            fd.write(response.content)
    else:
        print(f"Cannot download {url}: {response.status_code}")


def main():
    # Prepare an output saving directory
    data_dir = os.path.join(here, "data", "search")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Aaaand they're off!
    global stopwatch
    stopwatch.start()

    search_string = "language%3AYAML+%22kind%3A+Job%22"
    for term in terms:
        result_path = os.path.join(data_dir, f"results-{term}.json")
        zero_marker = f"{result_path}.0"
        if os.path.exists(result_path) or os.path.exists(zero_marker):
            continue
        print(f"Searching for term {term}")
        search_url = f"{search_string}+%22{term}%22"
        do_search(search_url, result_path)

    # Find all the files
    files = [x for x in os.listdir(data_dir) if ".0" not in x and "result" in x]
    print("Done parsing terms!")
    import IPython

    IPython.embed()

    # Next we need to download them, and we will do this based on repository
    job_dir = os.path.join(here, "data", "jobs")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Each file has a group of results, organized by search term
    for filename in files:
        filename = os.path.join(data_dir, filename)
        results = load_json(filename)

    # Each result has a repository and exact file path
    count = 0
    for result in results:
        repo_path = os.path.join(job_dir, result["repository"]["full_name"])
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
        job_file = os.path.join(repo_path, result["path"])
        job_repo_dir = os.path.dirname(job_file)
        if not os.path.exists(job_repo_dir):
            os.makedirs(job_repo_dir)

        count += 1
        # Don't re-download stuff we already have
        if os.path.exists(job_file):
            continue
        # The raw url removes blob
        raw_url = (
            result["html_url"]
            .replace("/blob", "")
            .replace("https://github.com", "https://raw.githubusercontent.com")
        )
        download(raw_url, job_file)

    # 900
    print(f"Done! Downloaded {count} job files.")


if __name__ == "__main__":
    main()
