import os
import time
from os.path import expanduser
from distutils.dir_util import copy_tree
import shutil
from .render_job import RenderJob 
from .render_job_status import RenderJobStatus

class RenderManager():
    
    def __init__(self, environment, batch_manager, blob_manager):
        self.environment = environment
        self.environment.validate()
        self.outputdir = expanduser('~/rendering/finished_renders')

        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

        self.batch_manager = batch_manager
        self.blob_manager = blob_manager

    def process_list(self, job_list, is_dry_run):
        print(RenderJob.get_str_header())

        for root in job_list.rootjobs:
            try:
                # We can ignore succeeded or failed jobs
                if root.status in [RenderJobStatus.Success, RenderJobStatus.Failed]:
                    continue

                root.prepare()

                # Uploading may change the status so we write out the same line twice
                print(str(root), end='\r')
                self._upload_if_required(job_list, root, False)
                print(str(root), end='\r')

                # Then leave it to this to write out the root job the final time
                self._schedule_jobs(job_list, root, is_dry_run)

                # Check the status of the jobs which have been scheduled
                self._check_cloud_statuses(job_list, root)

                # Downloado and assembly any rendered jobs
                self._process_downloads(job_list, root)
            
            except Exception as ex:
                print(ex)
                root.error = ex.args[0]
                self._set_job_status(job_list, root, RenderJobStatus.Failed)

    def _check_cloud_statuses(self, job_list, root):  
        self._update_job_status(job_list, root)
        for child in root.children:
            self._update_job_status(job_list, child)

    def _update_job_status(self, job_list, job):
        newstatus = self.batch_manager.get_transitioned_status(job)        
        self._set_job_status(job_list, job, newstatus)

    def _set_job_status(self, job_list, job, newstatus):
        if newstatus and job.status != newstatus:
            oldstatus = job.status
            job.status = newstatus
            self._persist(job_list)
            print(job, end='\r')

            print(f" ({oldstatus.name} -> {newstatus.name})")

    def _schedule_jobs(self, job_list, root, is_dry_run):
        if len(root.children) == 0:
            if not root.is_scheduled:
                if not is_dry_run:
                    self.batch_manager.schedule_job(root)
                    self._persist(job_list)
                    print(str(root))
                else:
                    self._print_dry_run_job(root)            
        else:
            print(str(root))
            for child in root.children:
                if not child.is_scheduled:
                    if not is_dry_run:
                        print(str(child), end='\r')
                        self.batch_manager.schedule_job(child)
                        self._persist(job_list)
                        print(str(child))
                    else:
                        self._print_dry_run_job(child)

    def _print_dry_run_job(self, job):
        print(f"Dry run, would have scheduled: -b {job.package} -S \"{job.scene}\" -x {job.xres} -y {job.yres} -s {job.samples} -p {job.percentage} -f {job.startframe} -e {job.endframe} -t {job.step}")

    def _persist(self, job_list):
        if job_list.can_save:
            job_list.save()

    def _upload_if_required(self, job_list, job, is_dry_run):
        if not job.is_uploaded and not is_dry_run:
            print("Uploading blend")
            self.blob_manager.upload_package(job)
            
            job.is_uploaded = True
            job.set_status(RenderJobStatus.Uploaded)
            self._persist(job_list)

    def _process_downloads(self, job_list, root):
        for child in root.children:
            self._download_if_required(job_list, child)

        self._download_if_required(job_list, root)

        self._assemble(job_list, root)

    def _download_if_required(self, job_list, job):
        if job.status != RenderJobStatus.Rendered:
            return

        self._set_job_status(job_list, job, RenderJobStatus.Fetching)

        try:    
            self.blob_manager.download_result(job)
            self._set_job_status(job_list, job, RenderJobStatus.Assembly)
        except Exception as ex:
            self._set_job_status(job_list, job, RenderJobStatus.Failed)
            job.error = ex.args[0]

        self._persist(job_list)
        print(str(job), end='\r')

    def _assemble(self, job_list, root):
        if root.status in [RenderJobStatus.Success, RenderJobStatus.Failed, RenderJobStatus.Running, RenderJobStatus.Scheduled]:
            return

        if len(root.children) == 0:
            if root.status == RenderJobStatus.Assembly:
                self._copy_to_output(root, root)
                self._mark_finished(job_list, root)
        else:
            still_waiting = False
            for child in root.children:
                if child.status == RenderJobStatus.Assembly:
                    self._copy_to_output(root, child)
                    self._mark_finished(job_list, child)
                elif child.status == RenderJobStatus.Success:
                    pass
                else:
                    still_waiting = True
                
            if not still_waiting:
                self._mark_finished(job_list, root)

    def _copy_to_output(self, root, job):
        output_dir = os.path.join(self.outputdir, self.get_output_dir(job))
        temp_dir = self.blob_manager.get_job_dir(job)

        copy_tree(temp_dir, output_dir)
        shutil.rmtree(temp_dir)

    def get_output_dir(self, job):
        return f"{job.package}-{job._make_alpha(job.scene)}-{job.xres}x{job.yres}s{job.samples}p{job.percentage}"

    def _mark_finished(self, job_list, job):
        self._set_job_status(job_list, job, RenderJobStatus.Success)
