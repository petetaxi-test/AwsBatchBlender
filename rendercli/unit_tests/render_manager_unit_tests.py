import unittest
from unittest.mock import MagicMock
import context
import src
from src.render_manager import RenderManager
from src.render_environment import RenderEnvironment
from src.render_job import RenderJob

class RenderManagerUnitTests(unittest.TestCase):

    def test_create_render_manager(self):
        s3 = self.get_s3_mock()
        m = RenderManager(self.get_test_environment(), s3=s3)
        self.assertEqual(s3.upload_file.call_count, 0)        

    def test_upload_job(self):
        s3 = self.get_s3_mock()
        m = RenderManager(self.get_test_environment(), s3=s3)
        m.upload_blend(self.get_test_job())
        self.assertEqual(s3.upload_file.call_count, 1)       

    def test_submit_job_dry_run(self):
        s3 = self.get_s3_mock()
        batch = self.get_batch_mock() 
        m = RenderManager(self.get_test_environment(), s3=s3, batch=batch)
        m.start_job(self.get_test_job(), True)
        self.assertEqual(batch.submit_job.call_count, 0)

    def test_submit_job(self):
        s3 = self.get_s3_mock()
        batch = self.get_batch_mock() 
        batch.submit_job = MagicMock(return_value = { 'jobId': 'AWSIDHERE' })

        m = RenderManager(self.get_test_environment(), s3=s3, batch=batch)
        j = self.get_test_job()
        m.start_job(j, False)
        
        self.assertEqual(batch.submit_job.call_count, 1)
        self.assertEqual(j.cloudid, 'AWSIDHERE')

    def get_test_environment(self):
        env = RenderEnvironment()
        env.queueName = 'TestQueue'
        env.jobDefinition = 'TestDefinition'
        env.sourceBucket = 'SourceBucket'
        env.resultsBucket = 'ResultsBucket'
        return env

    def get_s3_mock(self):
        s3 = MagicMock()
        s3.upload_file = MagicMock(return_value=None)
        return s3

    def get_batch_mock(self):
        batch = MagicMock()
        return batch

    def get_test_job(self):
        job = RenderJob()
        job.blend_path = '../test/TheRing.blend'
        job.scene = 'Scene'
        return job

if __name__ == '__main__':
    unittest.main()