import boto3
from typing import Dict, List, Optional, Any
import re

class CDKManager:
    """
    Helper class for managing CloudFormation stacks and outputs."""
    def __init__(
            self, 
            region: str = 'eu-west-2',
            profile: Optional[str] = None
        ):
        self.region = region
        self._cloudformation_client = None
        self._profile = profile
    
    @property
    def cloudformation(self):
        """Lazy-loaded CloudFormation client."""
        if not self._cloudformation_client:
            session = boto3.Session(
                profile_name=self._profile,
                region_name=self.region
            )
            self._cloudformation_client = session.client('cloudformation')
        return self._cloudformation_client
    
    def get_stack_export(self, stack_name: str, export_name: str) -> Optional[str]:
        """Get the value of a CloudFormation stack export."""
        response = self.cloudformation.list_exports()
        for export in response['Exports']:
            if export['Name'] == export_name and export['ExportingStackId'].endswith(stack_name):
                return export['Value']
        return None
    
    def _get_nested_stacks(self, master_stack_name: str) -> List[str]:
        """Get all nested stacks for a master stack."""
        stacks = []
        try:
            # First add the master stack
            stacks.append(master_stack_name)
            
            # Get all stacks and filter for nested ones
            paginator = self.cloudformation.get_paginator('list_stacks')
            for page in paginator.paginate(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE']):
                for stack in page['StackSummaries']:
                    # Check if this is a nested stack of our master stack
                    if 'ParentId' in stack and master_stack_name in stack['ParentId']:
                        stacks.append(stack['StackName'])
        except Exception as e:
            print(f"Error retrieving nested stacks: {e}")
        
        return stacks
    
    def get_all_outputs_by_format(self, master_stack_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all outputs from a master stack and its nested stacks that follow the format
        {category}-{parameter}-{name} in their description.
        
        Args:
            master_stack_name: The name of the master stack
            
        Returns:
            Dictionary of outputs organized by category and parameter
        """
        result = {}
        stacks = self._get_nested_stacks(master_stack_name)
        
        # Format pattern: {category}-{parameter}-{name}
        pattern = r'^([^-]+)-([^-]+)-(.+)$'
        
        for stack_name in stacks:
            try:
                response = self.cloudformation.describe_stacks(StackName=stack_name)
                for stack in response['Stacks']:
                    if 'Outputs' in stack:
                        for output in stack['Outputs']:
                            print(output)
                            if 'Description' in output and output['Description']:
                                match = re.match(pattern, output['Description'])
                                if match:
                                    category, parameter, name = match.groups()
                                    
                                    # Initialize nested dictionaries if needed
                                    if category not in result:
                                        result[category] = {}
                                    if parameter not in result[category]:
                                        result[category][parameter] = {}
                                    
                                    # Store the output value
                                    result[category][parameter][name] = {
                                        'Value': output['OutputValue'],
                                        'OutputName': output['OutputKey'],
                                        'StackName': stack_name
                                    }
            except Exception as e:
                print(f"Error retrieving outputs for stack {stack_name}: {e}")
        
        return result
    
    def get_parameter_outputs(self, master_stack_name: str, category: str, parameter: str) -> Dict[str, Any]:
        """
        Get all outputs for a specific category and parameter.
        
        Args:
            master_stack_name: The name of the master stack
            category: The output category to filter by
            parameter: The output parameter to filter by
            
        Returns:
            Dictionary of outputs matching the category and parameter
        """
        all_outputs = self.get_all_outputs_by_format(master_stack_name)
        
        # Return the specific category/parameter or empty dict if not found
        if category in all_outputs and parameter in all_outputs[category]:
            return all_outputs[category][parameter]
        return {}