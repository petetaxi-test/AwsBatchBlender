import os
import re
import uuid
import copy
from datetime import datetime
from colorama import Fore, Back, Style
from .render_job_status import RenderJobStatus

class RenderJob():
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.cloudid = ''
        self.description = ''
        self.key = ''
        self.source_blend_path = ''
        self.additional_file_count = 0
        self.package = '' 
        self.scene = ''
        self.xres = 1920
        self.yres = 1080
        self.samples = 32
        self.percentage = 10
        self.startframe = ''
        self.endframe = ''
        self.step = 1
        self.parent = None
        self.children = []
        self.is_uploaded = False
        self.status = RenderJobStatus.Pending
        self.error = None
        self.startedAt = None
        self.stoppedAt = None
        
    def prepare(self):
        if not self.package:
            raise Exception("Package not specified.")

        # Check in package directory
        # if not os.path.exists(self.blend_path):
        #     raise Exception("Blend file does not exist.")

        if not self.scene:
            raise Exception("Scene not specified.")

        self.key = self._make_key()

        for child in self.children:
            child.prepare()

    @property
    def is_root_job(self):
        return self.parent is None

    @property
    def is_scheduled(self):
        return self.cloudid

    @property   
    def frame_count(self):
        return self.endframe - self.startframe + 1

    def set_status(self, value):
        self.status = value

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        if not child.parent is self:
            raise Exception('Child does not belong to this parent.')
        if not child in self.children:
            raise Exception('Child not in children list, but was parented to this job.')
        child.parent = None
        self.children.remove(child)

    def make_child_copy(self, startframe, endframe, step):
        if not self.is_root_job:
            raise Exception('This is not a root job.')

        self.prepare()
        child = RenderJob()        
        child.package = self.package
        child.scene = self.scene
        child.xres = self.xres
        child.yres = self.yres
        child.samples = self.samples
        child.percentage = self.percentage
        child.startframe = startframe
        child.endframe = endframe
        child.step = step

        self.add_child(child)
        child.prepare()

    def to_dict(self):
        return {
            'id': str(self.id),
            'source_blend_path': self.source_blend_path,
            'description': self.description,
            'package': self.package,
            'additional_file_count': self.additional_file_count,
            'key': self.key,
            'scene': self.scene,
            'xres': self.xres,
            'yres': self.yres,
            'samples': self.samples,
            'percentage': self.percentage,
            'startframe': self.startframe,
            'endframe': self.endframe,
            'step': self.step,
            'is_uploaded': self.is_uploaded, 
            'status': self.status.name,
            'cloudid': self.cloudid,
            'children': list(map(lambda c: c.to_dict(), self.children)),
            'error': self.error,
            'startedAt': self.startedAt,
            'stoppedAt': self.stoppedAt
        }

    def break_job(self, num_frames):
        startframe = self.startframe

        while startframe <= self.endframe:
            endframe = startframe + (num_frames * self.step) - 1
            if endframe > self.endframe:
                endframe = self.endframe
            self.make_child_copy(startframe, endframe, self.step)
            startframe = endframe + 1
    
    def describe(self, include_headers=True, dates=False):
        if include_headers:
            print(RenderJob.get_str_header())
        
        print(str(self))
        if self.error:
            print('    ' + self.error)

        if dates:
            self._print_dates(self)
        
        if any(self.children):
            for child in self.children:
                child.describe(False)
                if dates:
                    self._print_dates(child)

    @classmethod
    def from_dict(cls, obj):
        result = RenderJob()
        result.id = obj['id']
        result.description = obj['description']
        result.source_blend_path = obj['source_blend_path']
        result.additional_file_count = obj['additional_file_count']
        result.package = obj['package']
        result.key = obj['key']
        result.scene = obj['scene']
        result.xres = int(obj['xres'])
        result.yres = int(obj['yres'])
        result.samples = int(obj['samples'])
        result.percentage = int(obj['percentage'])
        result.startframe = int(obj['startframe'])
        result.endframe = int(obj['endframe'])
        result.step = int(obj['step'])
        result.error = obj['error']
        result.startedAt = obj['startedAt']
        result.stoppedAt = obj['stoppedAt']

        if 'children' in obj.keys():
            result.children = list(map(lambda o: RenderJob.from_dict(o), obj['children']))
        
        result.is_uploaded = obj['is_uploaded'] in ['True', 'TRUE', 'true']
        result.status = RenderJobStatus(obj['status'])
        result.cloudid = obj['cloudid']
        
        for child in result.children:
            child.parent = result
        
        return result

    @classmethod
    def get_str_header(cls):
        return f"{Fore.WHITE + Style.BRIGHT}    {'Job':<30} {'Scene':<15} {'Start':<5} {'End':<5} {'Step':<5} {'Sam':<5} {'Pct':<4} {'Status':<9} AwsId"

    def __str__(self):
        colour_code = Style.NORMAL + (Fore.YELLOW if self.is_root_job else Fore.BLUE)
        parent_mark = '---' if self.is_root_job else ' \\-'
        blend_stub = self._first_and_last(self.description if self.description else self.package, 30)
        cloudid = '' if len(self.children) > 0 else self.cloudid 
        return f"{colour_code}{parent_mark} {blend_stub:<30} {self.scene[:15]:<15} {self.startframe:<5} {self.endframe:<5} {self.step:<5} {self.samples:<5} {self.percentage:<4} {self.status.name:<9} {cloudid}"

    def _first_and_last(self, string, length):
        whole_len = len(string)
        if whole_len <= length:
            return string
        else:
            start_len = length // 2
            end_len = length - start_len - 2
            return string[:start_len] + '..' + string[whole_len - end_len:]

    def _make_key(self):
        key = "{package}-{scene}-{xres}x{yres}s{samples}p{percentage}-from{startframe}to{endframe}j{step}" \
            .format(package = self.package, \
                scene = self._make_alpha(self.scene), \
                xres = self.xres, \
                yres = self.yres, \
                samples = self.samples, \
                percentage = self.percentage, \
                startframe = self.startframe, \
                endframe = self.endframe, \
                step = self.step)
        return key

    def _make_alpha(self, string):
        return re.sub(r'\W+', '', string)

    def _print_dates(self, job):
        if job.startedAt or job.stoppedAt:
            started = f"Started: {self._date_to_string(job.startedAt)}  " if job.startedAt else ''
            stopped = f"Stopped: {self._date_to_string(job.stoppedAt)}  " if job.stoppedAt else ''
            duration = ((int(job.stoppedAt) - int(job.startedAt)) / 1000.0) if job.startedAt and job.stoppedAt else -1
            durationStr = f"Duration: {str(duration)}s  " if duration > 0 else ''
            durationPerFrame = ''
            if duration > 0 and job.startframe > 0 and job.endframe > 0:
                framecount = job.endframe - job.startframe + 1
                durationPerFrame = f"Duration per frame: {duration/framecount}s"
            print(f"    {started}{stopped}{durationStr}{durationPerFrame}")
            
    def _date_to_string(self, intvalue):
        if not intvalue:
            return None
        ts = int(intvalue)
        ts /= 1000
        return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
