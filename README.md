# Blender AWS Batch

Author: Peter Reay

## Introduction

A simple implementation of rendering Blender files on AWS Batch, which can be configured (via the compute environment) to scale on your choice of EC2 instances to process your jobs.

All the benefits of AWS Batch

- Scale up and down (to zero) automatically.
- Automatic choice of EC2 instance types based on the options in your compute environment, and the number and configuration of jobs you submit.
- The default AMI which AWS Batch selects (for either normal or GPU jobs) includes all the NVIDIA drivers which are needed for CUDA processing. Blender and the CUDA toolkit are set up in the docker containers in this project.
- Simple CloudFormation setup in your AWS environment.

The jobs run in a docker container with Blender, the CUDA toolkit, and the nvidia drivers installed. You can customize the image if you like - see the docker-blenderbase and docker-blender directories, but you don't need to do this. My versions in the public repository should work - the RenderJobDefinition references a specific public version of this image.

There is also a cli interface for submitting and managing jobs from the client machine.

## Some warnings:

Have a glance through the `cloud-render-cloudformation.yml` template, and particularly ensure you're happy with the `ComputeResources` properties - rendering is going to cost money, and if you understand this you should understand your likely costs. The Minimum cVPUs should be 0 so nothing runs if there are no jobs to process. 

The max vCPUs of 16 and instance type of p3 will mean only a single p3.2xlarge instance will run, but you can scale up to any value you want, or use different instance types. If you're not using GPU instances, remove the `ResourceRequirements` from the JobDefinition, as this indicates a GPU is required to run a job (you can also increase the GPU count if you want).

Also: no guarantee is given for the correctness of this - it is just a proof-of-concept I've knocked up in the last few days. I would strongly recommend going into the EC2 console, and verifying that all the instances have indeed closed down after your renders are complete - or a problem could end up costing you a lot.

AWS Batch, and these scripts, are free - you just pay for the other AWS resources which are utilised. 

You might want to add a deletion policy for CloudWatch, where logs from the jobs are stored - e.g. delete them after a week, so you're not paying for storage.

## Setup

This should work on Mac/Win/Linux. Blender always runs on Linux in the docker container, but any client can be used for scheduling jobs.

### Prerequisites

It's assumed you have an Amazon Web Serivces (AWS) account, and you know how to get your API key.

You should have these installed first:

- Python 3.x 
- AWS CLI

If you haven't already, configure aws by typing `aws configure` and enter your AWS Access Key ID and AWS Secret Access Key, and choose your region. Important: choose a region which includes GPU accelerated instances, e.g. `eu-west-1` (Ireland). Or edit the job definition so GPUs aren't required.

### Deploy to AWS

To deploy to AWS, simply cd to the aws directory and enter this command, if you wish replacing `render-stack` with your chosen stack name (you'll use this name when deleting the stack or configuring the client). 

```sh
aws cloudformation deploy --template-file cloud-render-cloudformation.yml --stack-name render-stack --capabilities CAPABILITY_IAM
```

This will usually take a few minutes. If it fails, look in the CloudFormation console to see why.

If at any point you want to remove all the rendering resources from AWS (again use your stack name), use this command. Note it will fail if there are any files in your source/destination S3 buckets, so empty them before doing this.
```sh
aws cloudformation delete-stack --stack-name render-stack
```

You can deploy to multiple stacks in the same account if you so wish.

### Get output parameters from AWS

After deploying, run the render cli with your stack name to configure the client to use your cloud services.

```sh
cd rendercli
python src/render.py configure --stackname test-stack
```

Note: try `python3` if `python` doesn't work. 

This will save your AWS configuration in ~/.renderconfig

## Submitting a job

Pack all your resources into the blend file, and save it.

Now you're ready to submit a job.

```sh
cd rendercli

# Creates the joblist.csv file
python src/render.py init

# Add a job
python src/render.py add --blend ../test/TheRing.blend --scene Scene --samples 128 --percentage 100 --startframe 1 --endframe 2 --breaksize 1
```

The job is split into multiple render jobs if `--breaksize` is less than the number of frames to be rendered. You should see the `Pending` jobs listed on the console.

You can use the `describe` command to list the current state at any point. This only describes the content of the local job list, it doesn't contact AWS to check the state of jobs.

```sh
# Describe the local job list file
python src/render.py describe
```

Now to process your jobs use the `process` command.

```sh
# Upload, submit, check, and download jobs as appropriate
python src/render.py process
```

You should see your jobs uploaded and submitted, and you will get the AWS Batch job ids. If you have many jobs you can use that id to search for the job in the AWS Batch console.

Then periodically use the `process` command to check the status of the jobs, and download and assemble the rendered frames once they are complete.

## The Job file

By default, the render cli stores jobs in `./joblist.csv` though you can override this (for all comamnds) by specifying `--jobfile <FILE>` or `-j <FILE>`.

As the file is a CSV, you can manage your jobs in a spreadsheet e.g. Excel if you need to make changes to jobs. E.g. to re-run with a different sample count or percentage, you can change the states back to 'Pending' and update the job properties. This allows you to operate on multiple jobs at once. Make sure Excel doesn't have the file locked though when you have stuff to write to it.

## Watching your job as it is processed

- After submitting a job, if you look in the AWS Batch console, on the dashboard you should see a Runnable job on your queue (or Submitted, which should quickly move to Runnable). 

- Then, at some point the 'Desired vCPUs' in the Compute Environment will increase. This doesn't happen immediately, as AWS Batch waits to see if you submit more jobs, which could be run together on a larger EC2 instance. This can take longer the first time you're using a compute environment, so be patient at first. 

- Then, in ECS you see a cluster being created.

- Then, in EC2 you can see a Spot Request for the compute resources. You can tell if it has been *fullfilled* or whether it is waiting because the current spot price is above your threshold.

- Then, when the spot request is fullfilled, you should see an Instance in EC2.

- Your job will move to the Starting, then Running, then (hopefully) Succeeded state.

  - If the job fails, you can view the CloudWatch logs to see why.
  - Note: if it's not working, make sure you check that there are no EC2 instances still running. If you change the environment in which the jobs run, it can result in EC2 instances running which haven't properly joined the ECS cluster - this means they won't get shut down, and will cost you money!

- Once a job is complete, and your run the cli `process` command, it should download the result and, once all parts of a job are complete, assembly the results into ~/rendering/finished_renders/*jobname*

- A while later, the Desired vCPUs will drop again to zero, and the EC2 instance, and ECS cluster will shut down. Again, this doesn't happen immediately, in case you submit more jobs, but it should go down within a few minutes.

## Including additional files

If you have files which can't be packed into the blend, such as a video file to be used as a texture, you can add them to the job with the `-a <FILE>` argument when calling the `add` command. Any such files will be included in the root of the zip which is pushed to S3, and will thus be extracted into the same folder in the docker container. You should reference files using relative paths from your blend, and have them in the same directory.

## Extra hook scripts

Let's say you have some additional logic you want to run in the docker container before your job executes. For example, downloading additional files from S3 which are too bulky to include with every job. You can handle this using the `pre_render.sh` hook script. You should include this script in your job using the `-a` option described above. The script will run in bash with the current directory being the directory where the blend is extracted.

Similaryly use `post_render.sh` for post render actions. Anything you want to put in the output zip which is automatically uploaded, copy it to `/tmp/render_output`.