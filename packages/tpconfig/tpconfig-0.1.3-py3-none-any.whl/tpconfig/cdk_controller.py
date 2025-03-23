import boto3

class CDKManager:
    def __init__(
            self, 
            region: str = 'us-east-1'
        ) -> None:
        self.region = region
    
    def get_stack_export(self, stack_name: str, export_name: str) -> str:
        """Get the value of a CloudFormation stack export."""
        client = boto3.client('cloudformation', region_name=self.region)
        response = client.list_exports()
        for export in response['Exports']:
            if export['Name'] == export_name and export['ExportingStackId'].endswith(stack_name):
                return export['Value']
        return None