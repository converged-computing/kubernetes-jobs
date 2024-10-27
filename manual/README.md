# What features are we missing in HPC jobs?

> Manual parsing of Job / JobSet to assess features

The automated approaches are nice, but I want to go through the Job and JobSet directives and make a simple listing of the features that are supported (and note what is not supported for HPC workload managers):

## Summary

```bash
kubectl explain job
kubectl explain job.metadata
kubectl explain job.spec
# note that just template is fairly sparse, and template.metadata is similar to job.metadata
kubectl explain job.spec.template.spec

kubectl explain job.spec.template.spec.containers
kubectl explain job.spec.template.spec.volumes

kubectl explain job.status

# kubectl apply --server-side -f https://github.com/kubernetes-sigs/jobset/releases/download/v0.7.0/manifests.yaml
kubectl explain jobset
```

These are the things Kubernetes jobs have that we don't have in HPC:

### Metadata

- **Versioning**: The entire representation of the job is in YAML, and it's versioned. We don't have that in HPC, our job scripts are kind of messy and it's not clear which have features that are/aren't supported over time (is that something we care to know about? Are scripts backwards compatible?)
- **Labels**: that add additional functionality, just by way of being present.
- **Owner**: The abstraction of an owner that is another kind of job abstraction (beyond the user)
- **Metadata**: Some workload managers don't make complete metadata programatically accessible. With K8s you can get everything via API calls, in json/yaml, etc.

### Job

- **backoff** A number of retries of the job (up to a limit), assumes that failures can be due to ephemeral reasons
- **Parallelism**: This one is probably surprising, but I am going to put "easy" parallelism because I don't think it's as easy in HPC as it is in cloud. In Kubernetes, you just set indexed to a number. In HPC running something in parallel is always something to figure out (again). In Kubernetes Job, this is also not just the number of total jobs, but the maximum number of pods to be running at once. Based on policies these might be recreated, etc.
- **Controller or managed by**: This (in HPC) would be the workflow tool. In Kubernetes, this is the operator - what is managing the job. We have the same idea, it's just messy and not kept (after the fact) with the job (for the most part). You might be able to figure out that something was run with, for example, Snakemake, based on the output structure and file naming, but this isn't a consistent standard.
- **Completions**: "Run this thing X times to consider success." This would be akin to something we'd see in MuMMI - we want to keep running something until we get a number of successful completions (or some state). 
- **Maximum failed**: Akin to completions, this is saying "Only allow this number of failed before we quit"
- **Failure policy**: Conditions to fail a pod.
- **Success policy**: Conditions to mark a pod as completed (success)
- **restart Policy**: how to restart (Never, Always, OnFailure)
- **Replacement policy**: Similar to the above, but specifies when to create replacement pods and retry.
- **Suspend**: This is akin to saying "Pause"- in Kubernetes we don't send the pods to be scheduled. This is the trick that Kueue uses to shuffle things around before releasing. If a job running is suspended, running stuff is completed and the start time and active deadline seconds (duration) are reset.
- **Lifecycle events**: these would be akin to prolog and other job events. It's just easier to do in Kubernetes.
- **affinity**: These are scheduling constraints. We have them in HPC but my impression is that they aren't widely used, and if they are, it's an expert move. 
- **service accounts**: In HPC this would be akin to a LICENSE or some token to use an API that is not available to all users.
- **Injection of links**: this could be environment or similar, but it says "inject these envars into my job for this service, or these secrets." This would be nice if, for example, a user could add a label to a job that prepares it for a specific context, and then switch easily for another context. I had a prototype for this (for containers) with a tool called [paks](https://github.com/syspack/paks) that could load named environments into running containers.
- **containers**: Not sure this counts, but Kubernetes is based on pods->containers. It's reproducible in that sense, and that's the native unit of operation. The native unit of operation for HPC is... a binary.
- **node selectors**: some HPC workload managers don't let you select groups of nodes based on some criteria. This is easy to do in Kubernetes.
- **os**: you can specify the Os of the container on the fly (didn't know you could do that, I wonder why you would need to, need to read more about it)
- **runtime class**: I understand this better now reading about snapshotters, etc. This is custom logic for basically how you want your container prepared. For snapshotters, for example, you can specify a custom snapshotter.
- **priority class names**: I think we have priority in HPC, but it's usually just a number, not a human interpretable thing.
- **readiness gates**: "Don't consider this job or service ready to run until these criteria are achieved" [spec](https://github.com/kubernetes/enhancements/tree/master/keps/sig-network/580-pod-readiness-gates)
- **resource claims**: This is how to currently specify needing specific devices, sometimes with topology - this is in alpha and requires the dynamic resource allocation feature gate.
- **scheduler name**: ask for a custom scheduler. Most HPC workload managers don't support this. Flux does, but we don't really have many options for other schedulers aside from sched simple, which reduces features but will give you faster throughput (I think).
- **scheduling gates**: akin to readiness gates, but for the scheduler
- **security context**: pod-level security attributes. We should look into this more.
- **termination grace period**: seconds to terminate gracefully (e.g, to allow cleanup)
- **topology spread constraints**: I'm sure Flux could do this, but I (and maybe most) don't know how to do it.
- **resources on demand**: In HPC, we have filesystems that are there or not. Actually, with flux rabbits we can ask for node local storage on demand (and that actually uses Kubernetes)! But what we don't easily have is "attach this resource on demand" whether that be volumes, drivers, network, or other hardware. The systems are more hard coded, if that makes sense.

### Volumes

Generally speaking, a volume has a lot more meaning in cloud. For example, I can have another cloud service provide it (e.g., storage) or even a GitHub repository. I can also define a CSI (container storage interface) that describes how to do some kind of special volume handling.

### Containers

- **environment from**: "Get my envars from this place aside from me hard coding in the script"
- **lifecycle events**: On start / terminate / other event do this
- **probes**: for liveness or readiness - "Do this check to make sure we are OK"
- **ports**: "My job needs these ports exposed / use in this way
- **resources**: "I am going to define these custom labels / selectors to ask for specific resources for my job (we obviously have this, but it's not a consistent format or often easy to use)
- **restart policy**: akin to the job restart policy
- **security context**: ditto
- **termination logs**: we have error logs, but this is subtly different - a path to write failure messages and how to write them.

### Job Status

This is akin to events, and would be nice to have more events, generally speaking, for HPC.

- **partial completion**: e.g., "This many completions were successful, this many restarted, etc." We typically have all or nothing final states.
- **conditions**: custom conditions that can be controlled by an operator, depending on the kind of object.

## Jobset

- **coordinator**: a pod can be assigned to coordinate a group of jobs
- **network**: network details for a group of jobs
- **replicated jobs**: the group of jobs in the set

JobSet also has policies and suspend, with more features than job, because you can target jobs and specify basic dependencies.
