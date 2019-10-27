import csv
from src.render_job import RenderJob

class RenderJobList:

    def __init__(self):
        self.rootjobs = []
        self.path = None

    @classmethod
    def from_dict(cls, obj):
        result = RenderJobList()
        result.rootjobs = list(map(lambda j: RenderJob.from_dict(j), obj['rootjobs']))
        return result

    @property
    def can_save(self):
        return not self.path is None

    @classmethod
    def load(cls, path):
        result = RenderJobList()
        result.path = path
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                job = RenderJob.from_dict(row)
                
                parentid = row['parent']
                if parentid:
                    parent = next((x for x in result.rootjobs if x.id == parentid), None)
                    if parent is None:
                        raise Exception(f'Parent "{parentid}" not found."')
                    parent.add_child(job)
                else:
                    result.rootjobs.append(job)
        return result

    def save_as(self, path):
        self._save_as_csv(path)
        self.path = path

    def save(self):
        if self.path is None:
            raise Exception('File has no path, use save_as(path).')

        self.save_as(self.path)
    
    def append(self, job):
        self.rootjobs.append(job)

    def describe(self, dates=False):
        print(RenderJob.get_str_header())
        self._describe_jobs(self.rootjobs, dates=dates)

    def prepare(self):
        for job in self.rootjobs:
            job.prepare()

    def break_jobs(self, num_frames):
        for job in self.rootjobs:
            if job.is_scheduled or any(job.children):
                continue
            if job.frame_count > num_frames:
                job.break_job(num_frames)

    def to_dict(self):
        return {'rootjobs': list(map(lambda x: x.to_dict(), self.rootjobs)) }

    def _describe_jobs(self, joblist, dates=False):
        for job in joblist:
            job.describe(False, dates=dates)

    def _save_as_csv(self, path):
        with open(path, 'w') as f:
            first_as_dict = RenderJob().to_dict()
            del first_as_dict['children']
            first_as_dict['parent'] = ""
            keys = first_as_dict.keys()

            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()

            self._write_csv_rows(writer, self.rootjobs)

    def _write_csv_rows(self, writer, list):
        for job in list:
            self._write_csv_row(writer, job)
            self._write_csv_rows(writer, job.children)

    def _write_csv_row(self, writer, job):
        item_as_dict = job.to_dict()
        del item_as_dict['children']
        item_as_dict['parent'] = job.parent.id if not job.parent is None else ''
        writer.writerow(item_as_dict)

    