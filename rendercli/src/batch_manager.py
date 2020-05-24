import boto3
from .render_job import RenderJob 
from .render_job_status import RenderJobStatus

class BatchManager():

    def __init__(self, environment, batch=None):
        self.environment = environment
        self.batch = boto3.client('batch') if batch is None else batch

    def schedule_job(self, job):
        # Give the job a name
        job.prepare()
    
        # Submit the job to AWS Batch
        job.cloudid = self._submit_batch_job(job)
        job.set_status(RenderJobStatus.Scheduled)
        job.just_scheduled = True

    def _submit_batch_job(self, job):
        response = self.batch.submit_job(
            jobName = job.key,
            jobQueue = self.environment.queueName,
            jobDefinition = self.environment.jobDefinition,
            parameters = {
                'blend': job.package,
                'scene': job.scene,
                'xres': str(job.xres),
                'yres': str(job.yres),
                'samples': str(job.samples),
                'percentage': str(job.percentage),
                'startframe': str(job.startframe),
                'endframe': str(job.endframe),
                'step': str(job.step)
            }
        )
        return response['jobId']
    
    def get_transitioned_status(self, job):
        if not self._requires_cloud_check(job):
            return None

        awsstatus, reason, startedAt, stoppedAt = self._get_cloud_job_status(job)
        job.startedAt = startedAt
        job.stoppedAt = stoppedAt

        if awsstatus == 'RUNNING':
            return RenderJobStatus.Running
        elif awsstatus == 'SUCCEEDED' and (job.status == RenderJobStatus.Running or job.status == RenderJobStatus.Scheduled):
            return RenderJobStatus.Rendered
        elif awsstatus == 'FAILED':
            job.error = reason
            return RenderJobStatus.Failed
        else:
            return None

    def _get_cloud_job_status(self, job):
        if not job.cloudid:
            raise "This job doesn't have a cloud job identifier."
        response = self.batch.describe_jobs(jobs=[job.cloudid])
        if len(response['jobs']) == 0:
            return RenderJobStatus.Failed
        awsjob = response['jobs'][0]
        awsstatus = awsjob['status']
        reason = awsjob['statusReason'] if 'statusReason' in awsjob.keys() else None
        startedAt = awsjob['startedAt'] if 'startedAt' in awsjob.keys() else None
        stoppedAt = awsjob['stoppedAt'] if 'stoppedAt' in awsjob.keys() else None
        return awsstatus, reason, startedAt, stoppedAt

    def _requires_cloud_check(self, job):
        return job.status in [RenderJobStatus.Scheduled, RenderJobStatus.Running]