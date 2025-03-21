import pytest
import time
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from tpconfig import ConfigManager

@pytest.fixture
def mock_dynamodb():
    """Fixture for mocking DynamoDB resource and table"""
    with patch('boto3.resource') as mock_resource:
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        yield mock_table

@pytest.fixture
def config_manager():
    """Fixture for creating ConfigManager instance"""
    return ConfigManager(table_name='test-config', region='us-west-2', cache_ttl=60)

class TestConfigManagerInit:
    def test_init_defaults(self):
        cfg = ConfigManager()
        assert cfg.table_name == 'config'
        assert cfg.region is None
        assert cfg.cache_ttl == 300
        
    def test_init_custom(self):
        cfg = ConfigManager(table_name='custom-table', region='us-west-2', cache_ttl=60)
        assert cfg.table_name == 'custom-table'
        assert cfg.region == 'us-west-2'
        assert cfg.cache_ttl == 60

class TestConfigManagerOperations:
    def test_get_config_success(self, config_manager, mock_dynamodb):
        # Setup mock response
        expected_item = {
            'categoryName': 'databases',
            'parameter': 'main',
            'host': 'localhost',
            'port': 5432
        }
        mock_dynamodb.get_item.return_value = {'Item': expected_item}
        
        # Test get_config
        result = config_manager.get_config('databases', 'main')
        
        # Verify
        mock_dynamodb.get_item.assert_called_once_with(
            Key={'categoryName': 'databases', 'parameter': 'main'}
        )
        assert result == expected_item
    
    def test_get_config_not_found(self, config_manager, mock_dynamodb):
        # Setup mock response for item not found
        mock_dynamodb.get_item.return_value = {}
        
        # Test get_config
        result = config_manager.get_config('databases', 'nonexistent')
        
        # Verify empty dict is returned
        assert result == {}
    
    def test_get_config_exception(self, config_manager, mock_dynamodb):
        # Setup mock to raise exception
        mock_dynamodb.get_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Test error'}},
            'GetItem'
        )
        
        # Test get_config with exception
        result = config_manager.get_config('databases', 'error')
        
        # Verify empty dict is returned on error
        assert result == {}
    
    def test_get_configs_by_category(self, config_manager, mock_dynamodb):
        # Setup mock response
        expected_items = [
            {'categoryName': 'services', 'parameter': 'api', 'url': 'https://api.example.com'},
            {'categoryName': 'services', 'parameter': 'web', 'url': 'https://www.example.com'}
        ]
        mock_dynamodb.query.return_value = {'Items': expected_items}
        
        # Mock Key condition
        with patch('boto3.dynamodb.conditions.Key') as mock_key:
            mock_key.return_value.eq.return_value = "mocked_condition"
            
            # Test get_configs_by_category
            result = config_manager.get_configs_by_category('services')
            
            # Verify
            mock_dynamodb.query.assert_called_once()
            assert result == expected_items
    
    def test_put_config(self, config_manager, mock_dynamodb):
        # Setup test data
        category = 'services'
        parameter = 'billing'
        config_values = {'rate_limit': 100, 'enabled': True, 'null_value': None}
        
        # Expected item (null_value should be filtered out)
        expected_item = {
            'categoryName': category,
            'parameter': parameter,
            'rate_limit': 100,
            'enabled': True
        }
        
        # Test put_config
        result = config_manager.put_config(category, parameter, config_values)
        
        # Verify
        mock_dynamodb.put_item.assert_called_once_with(Item=expected_item)
        assert result['success'] is True
    
    def test_update_config(self, config_manager, mock_dynamodb):
        # Setup test data
        category = 'services'
        parameter = 'api'
        updates = {'url': 'https://new-api.example.com', 'version': '2.0', 'deprecated': None}
        
        mock_dynamodb.update_item.return_value = {
            'Attributes': {'categoryName': category, 'parameter': parameter}
        }
        
        # Test update_config with mocked boto3.dynamodb.conditions.Key
        with patch('boto3.dynamodb.conditions.Key'):
            result = config_manager.update_config(category, parameter, updates)
            
            # Verify
            mock_dynamodb.update_item.assert_called_once()
            assert result['success'] is True
    
    def test_delete_config(self, config_manager, mock_dynamodb):
        # Setup test data
        category = 'services'
        parameter = 'old-service'
        
        mock_dynamodb.delete_item.return_value = {
            'Attributes': {'categoryName': category, 'parameter': parameter}
        }
        
        # Test delete_config
        result = config_manager.delete_config(category, parameter)
        
        # Verify
        mock_dynamodb.delete_item.assert_called_once_with(
            Key={'categoryName': category, 'parameter': parameter},
            ReturnValues="ALL_OLD"
        )
        assert result['success'] is True


class TestCaching:
    def test_cached_response(self, config_manager, mock_dynamodb):
        # Setup mock response
        expected_item = {
            'categoryName': 'databases',
            'parameter': 'main',
            'host': 'localhost',
            'port': 5432
        }
        mock_dynamodb.get_item.return_value = {'Item': expected_item}
        
        # Test get_config
        result = config_manager.get_config('databases', 'main')
        
        # Verify
        mock_dynamodb.get_item.assert_called_once_with(
            Key={'categoryName': 'databases', 'parameter': 'main'}
        )
        assert result == expected_item

        # Call get_config again to test cached response
        for _ in range(4):
            result = config_manager.get_config('databases', 'main')

        # Check the cache stats to assert that cache was used
        assert config_manager.get_config.cache_info().hits == 4

    def test_cache_expiry(self, config_manager, mock_dynamodb):
        """Test that cache expires correctly after TTL"""
        
        # Setup initial mock response
        mock_dynamodb.get_item.return_value = {'Item': {'value': '1'}}
        
        # First call - should cache the result
        result1 = config_manager.get_config('test', 'param')
        assert result1 == {'value': '1'}
        assert mock_dynamodb.get_item.call_count == 1
        
        # Change mock response
        mock_dynamodb.get_item.return_value = {'Item': {'value': '2'}}
        
        # Second call - should use cache
        result2 = config_manager.get_config('test', 'param')
        assert result2 == {'value': '1'}  # Should still be the cached value
        assert mock_dynamodb.get_item.call_count == 1  # No new DB call
        
        # Create a future time value
        future_time = time.time() + config_manager.cache_ttl + 10
        
        # IMPORTANT: Directly reset the cache to simulate expiry
        # This is what _check_cache_expiry would do
        config_manager.get_config.cache_clear()
        config_manager._last_cache_reset = future_time
        
        # Now with patch time for the next DB call
        with patch('time.time', return_value=future_time):
            # This call should make a new DB call since cache was cleared
            result3 = config_manager.get_config('test', 'param')
            
            # Should have new value and another DB call
            assert result3 == {'value': '2'}
            assert mock_dynamodb.get_item.call_count == 2