import shutil
import zipfile
import os
from os.path import expanduser
import tempfile
import boto3
import botocore
from botocore.exceptions import ClientError

class BlobManager():

    def __init__(self, environment, s3=None, workdir=None):
        self.environment = environment
        self.s3 = boto3.client('s3') if s3 is None else s3
        self.workdir = workdir if workdir else expanduser('~/rendering/work')
        self.package_dir = expanduser('~/rendering/packages')

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

    def upload_package(self, job):
        """Upload the blend file for this job, replacing it if it already exists."""
        filename = self._get_blend_name(job)
        package_path = os.path.join(self.package_dir, filename)

        if not self._file_exists(self.environment.sourceBucket, filename):
            self.s3.upload_file(package_path, self.environment.sourceBucket, filename)

    def get_job_dir(self, job):
        return os.path.join(self.workdir, job.key)

    def _get_blend_name(self, job):
        return f'Job.{job.package}.zip'

    def _get_zip_name(self, job):
        return f'Job.{job.key}.Results.zip'

    def _file_exists(self, bucket, key):
        s3 = boto3.client('s3')
        try:
            s3.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False
