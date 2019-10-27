from enum import Enum

class RenderJobStatus(Enum):
    Pending = 'Pending'
    Uploaded = 'Uploaded'
    Scheduled = 'Scheduled'
    Running = 'Running'
    Rendered = 'Rendered'
    Fetching = 'Fetching'
    Assembly = 'Assembly'
    Success = 'Success'
    Failed = 'Failed'