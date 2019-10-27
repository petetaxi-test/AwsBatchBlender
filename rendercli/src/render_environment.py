import json
from os.path import expanduser

class RenderEnvironment():

    def __init__(self):
        self.queueName = None
        self.jobDefinition = None
        self.sourceBucket = None
        self.resultsBucket = None

    def validate(self):
        if self.queueName is None:
            raise Exception('Queue name not set.')

        if self.jobDefinition is None:
            raise Exception('Job definition not set.')

        if self.sourceBucket is None:
            raise Exception('Source bucket not set.')

        if self.resultsBucket is None:
            raise Exception('Results bucket not set.')
    
    @classmethod
    def load(cls, path=None):
        with open(cls._get_path(path), 'r') as f:
            text = f.read()
            obj = json.loads(text)
            return RenderEnvironment._from_dict(obj)

    @classmethod
    def _from_dict(cls, obj):
        env = RenderEnvironment()
        env.queueName = obj['queueName']
        env.jobDefinition = obj['jobDefinition']
        env.sourceBucket = obj['sourceBucket']
        env.resultsBucket = obj['resultsBucket']
        return env

    @classmethod
    def from_stack_outputs(cls, outputs):
        env = RenderEnvironment()
        env.queueName = RenderEnvironment._after_last_slash(outputs['RenderJobQueue'])
        env.jobDefinition = RenderEnvironment._after_last_slash(outputs['RenderJobDefinition'])
        env.sourceBucket = outputs['SourceBucket']
        env.resultsBucket = outputs['ResultsBucket']
        return env

    @classmethod
    def _after_last_slash(cls, string):
        index = string.rfind('/')
        if index <= 0:
            return string
        else:
            return string[index + 1:]

    def save(self, path=None):
        text = json.dumps(self._to_dict())
        with open(self._get_path(path), 'w') as f:
            f.write(text)

    def _to_dict(self):
        return {
            'queueName': self.queueName,
            'jobDefinition': self.jobDefinition,
            'sourceBucket': self.sourceBucket,
            'resultsBucket': self.resultsBucket
        }

    @classmethod
    def _get_path(cls, specified_path):
        if specified_path:
            return specified_path
        else:
            return expanduser('~/.renderconfig')