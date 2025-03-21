import boto3
import json
from typing import Dict, Any, Optional, List, Union
from functools import lru_cache
import time

class ConfigManager:
    """
    Centralized configuration management for Nopaque services.
    Uses DynamoDB as a backend store.
    
    Example:
        # Get configuration
        config = ConfigManager()
        db_config = config.get_config('databases', 'main')
        
        # Update configuration
        config.put_config('services', 'billing', {'rate_limit': 100})
    """
    
    def __init__(self, table_name: str = 'config', region: Optional[str] = None, 
                 cache_ttl: int = 300):
        """
        Initialize the config manager.
        
        Args:
            table_name: Name of the DynamoDB config table
            region: AWS region (defaults to boto3 default region)
            cache_ttl: Time in seconds to cache config values (0 to disable)
        """
        self.table_name = table_name
        self.region = region
        self.cache_ttl = cache_ttl
        self._dynamodb_resource = None
        self._table = None
        self._last_cache_reset = time.time()
    
    @property
    def dynamodb(self):
        """Lazy-loaded DynamoDB resource."""
        if not self._dynamodb_resource:
            kwargs = {}
            if self.region:
                kwargs['region_name'] = self.region
            self._dynamodb_resource = boto3.resource('dynamodb', **kwargs)
        return self._dynamodb_resource
    
    @property
    def table(self):
        """Lazy-loaded DynamoDB table resource."""
        if not self._table:
            self._table = self.dynamodb.Table(self.table_name)
        return self._table
    
    def _check_cache_expiry(self):
        """Reset cache if TTL has expired."""
        if self.cache_ttl > 0 and time.time() - self._last_cache_reset > self.cache_ttl:
            self.get_config.cache_clear()
            self.get_configs_by_category.cache_clear()
            self._last_cache_reset = time.time()
    
    @lru_cache(maxsize=100)
    def get_config(self, category_name: str, parameter: str) -> Dict[str, Any]:
        """
        Get configuration by category and parameter.
        
        Args:
            category_name: The configuration category
            parameter: The specific parameter within the category
            
        Returns:
            Dict containing configuration values (empty dict if not found)
        """
        self._check_cache_expiry()
        try:
            response = self.table.get_item(
                Key={
                    'categoryName': category_name,
                    'parameter': parameter
                }
            )
            return response.get('Item', {})
        except Exception as e:
            print(f"Error retrieving config {category_name}/{parameter}: {e}")
            return {}
    
    @lru_cache(maxsize=20)
    def get_configs_by_category(self, category_name: str) -> List[Dict[str, Any]]:
        """
        Get all configurations for a specific category.
        
        Args:
            category_name: The configuration category
            
        Returns:
            List of configuration items in the category
        """
        self._check_cache_expiry()
        try:
            response = self.table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('categoryName').eq(category_name)
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error retrieving configs for category {category_name}: {e}")
            return []
    
    def put_config(self, category_name: str, parameter: str, 
                  config_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update configuration.
        
        Args:
            category_name: The configuration category
            parameter: The specific parameter within the category
            config_values: Dictionary of configuration values to store
            
        Returns:
            Response from DynamoDB
        """
        # Clear cache when updating
        self.get_config.cache_clear()
        self.get_configs_by_category.cache_clear()
        
        try:
            # Create item with proper keys
            item = {
                'categoryName': category_name,
                'parameter': parameter,
            }
            
            # Add all config values, filtering out None values
            for key, value in config_values.items():
                if value is not None:
                    item[key] = value
            
            response = self.table.put_item(Item=item)
            return {'success': True, 'response': response}
        except Exception as e:
            print(f"Error putting config {category_name}/{parameter}: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_config(self, category_name: str, parameter: str, 
                     updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update specific fields in a configuration item.
        
        Args:
            category_name: The configuration category
            parameter: The specific parameter within the category
            updates: Dictionary of values to update
            
        Returns:
            Response from DynamoDB
        """
        # Clear cache when updating
        self.get_config.cache_clear()
        self.get_configs_by_category.cache_clear()
        
        try:
            # Build update expression
            update_parts = []
            expr_values = {}
            expr_names = {}
            
            for key, value in updates.items():
                # Skip categoryName and parameter as they are keys
                if key in ('categoryName', 'parameter'):
                    continue
                    
                # Handle None values as removes
                if value is None:
                    update_parts.append(f"REMOVE #{key}")
                    expr_names[f"#{key}"] = key
                else:
                    update_parts.append(f"SET #{key} = :{key}")
                    expr_names[f"#{key}"] = key
                    expr_values[f":{key}"] = value
            
            # No updates to make
            if not update_parts:
                return {'success': True, 'message': 'No updates needed'}
                
            update_expression = " ".join(update_parts)
            
            response = self.table.update_item(
                Key={
                    'categoryName': category_name,
                    'parameter': parameter
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values if expr_values else None,
                ReturnValues="ALL_NEW"
            )
            
            return {
                'success': True, 
                'response': response,
                'updated_item': response.get('Attributes', {})
            }
        except Exception as e:
            print(f"Error updating config {category_name}/{parameter}: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_config(self, category_name: str, parameter: str) -> Dict[str, Any]:
        """
        Delete a configuration item.
        
        Args:
            category_name: The configuration category
            parameter: The specific parameter within the category
            
        Returns:
            Response from DynamoDB
        """
        # Clear cache when deleting
        self.get_config.cache_clear()
        self.get_configs_by_category.cache_clear()
        
        try:
            response = self.table.delete_item(
                Key={
                    'categoryName': category_name,
                    'parameter': parameter
                },
                ReturnValues="ALL_OLD"
            )
            return {
                'success': True, 
                'response': response,
                'deleted_item': response.get('Attributes', {})
            }
        except Exception as e:
            print(f"Error deleting config {category_name}/{parameter}: {e}")
            return {'success': False, 'error': str(e)}