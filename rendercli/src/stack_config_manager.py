import boto3

class StackConfigManager():

    def __init__(self, cloudformation=None):
        self.cloudformation = cloudformation if cloudformation else boto3.client('cloudformation')

    def get_outputs(self, stack_name):
        response = self.cloudformation.describe_stacks(StackName=stack_name)
        list_of_outputs = response['Stacks'][0]['Outputs']
        result = {}
        for pair in list_of_outputs:
            result[pair['OutputKey']] = pair['OutputValue']
        return result