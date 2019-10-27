import shutil
import zipfile
import os
from os.path import expanduser
import tempfile
import boto3
import botocore

class BlobManager():

    def __init__(self, environment, s3=None, workdir=None):
        self.environment = environment
        self.s3 = boto3.client('s3') if s3 is None else s3
        self.workdir = workdir if workdir else expanduser('~/rendering/work')

        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)

    def download_result(self, job):
        job.prepare()
        job_dir = self.get_job_dir(job)
        
        if not os.path.exists(job_dir):
            os.mkdir(job_dir)

        zip_path = os.path.join(job_dir, 'job.zip')
        results_object = self._get_zip_name(job)

        self.s3.download_file(self.environment.resultsBucket, results_object, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(job_dir)

        os.remove(zip_path)

    def upload_blend(self, job):
        """Upload the blend file for this job, replacing it if it already exists."""
        job.prepare()
        with tempfile.TemporaryDirectory() as tmpdirname:
            blend_for_zip = os.path.join(tmpdirname, 'job.blend')
            shutil.copy2(job.blend_path, blend_for_zip)

            job_file = self._get_blend_name(job)
            zip_path = os.path.join(tmpdirname, job_file)    
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(blend_for_zip, arcname='job.blend')

            self.s3.upload_file(zip_path, self.environment.sourceBucket, job_file)

    def get_job_dir(self, job):
        return os.path.join(self.workdir, job.name)

    def _get_blend_name(self, job):
        return f'Job.{job.blend_name}.zip'

    def _get_zip_name(self, job):
        return f'Job.{job.name}.Results.zip'


