import context
import src
import json
from colorama import Fore, Style
from src.render_job import RenderJob
from src.render_manager import RenderManager
from src.render_environment import RenderEnvironment
from src.render_job_list import RenderJobList
from src.batch_manager import BatchManager
from src.blob_manager import BlobManager

env = RenderEnvironment()

# The name of the AWS Batch Job Queue
# NOT the full ARN - just the queue name
env.queueName = 'RenderJobQueue-55d7f607de85a96'

# Name and version of the Batch Job Definition
# NOT the full ARN - just the definition name and version
# name:version
env.jobDefinition = 'RenderJobDefinition-98c5948957d351e:1'

# S3 Bucket where blend files are zipped and placed
env.sourceBucket = 'render-stack-renderblendbucket-hptilyppaye6'

# S3 Bucket where render output (images, zipped) are placed
env.resultsBucket = 'render-stack-renderresultsbucket-ny11b5o2f4eg'

# Details of the job to render

def create_job_list():
    job = RenderJob()

    job.blend_path = "../test/TheRing.blend"
    job.scene = 'Scene'
    job.percentage = 25
    job.samples = 32
    job.startframe = 1
    job.endframe = 10

    joblist = RenderJobList()
    joblist.append(job)

    joblist.prepare()
    joblist.break_jobs(5)
    joblist.describe()

    joblist.save_as('joblist.csv')

def describe_jobs():
    l = RenderJobList.load('joblist.csv')
    l.describe()

def start_jobs():
    l = RenderJobList.load('joblist.csv')

    m = RenderManager(env, BatchManager(env), BlobManager(env))
    m.process_list(l, True)

try:
    #create_job_list()
    # describe_jobs()
    start_jobs()
finally: 
    # TODO string printing better way
    print(Fore.RESET + Style.RESET_ALL)

# print('Started job: {0} with id {1}'.format(job.name, job.cloudid))