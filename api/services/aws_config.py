"""
Centralized AWS configuration and client management for tenx_job_recommender.

This module provides a unified interface for creating AWS clients and sessions
across the entire application, ensuring consistent configuration and credentials handling.
"""

import os
import json
import boto3
from typing import Optional, Dict, Any
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))


# Configuration
region_name = os.environ.get('AWS_REGION_NAME', 'us-east-1')
envdir = os.environ.get('ENVDIR', '.envdir')

# AWS configuration with retry settings
my_config = Config(
    region_name=region_name,
    signature_version='s3v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

# Global clients cache
_clients_cache: Dict[str, Any] = {}
_sessions_cache: Dict[str, Any] = {}


def get_aws_profile() -> Optional[str]:
    """
    Detect AWS profile similar to bash script logic.
    Checks for ~/.aws/config and returns appropriate profile name.
    
    Returns:
        Optional[str]: Profile name if found, None otherwise
    """
    aws_config_path = os.path.expanduser('~/.aws/config')
    aws_profile_name = os.environ.get('AWS_PROFILE_NAME', 
                                    os.environ.get('profile_name', 'ustenac'))
    
    if os.path.exists(aws_config_path):
        try:
            with open(aws_config_path, 'r') as f:
                config_content = f.read()
                if aws_profile_name in config_content:
                    logger.good(f"Found {aws_profile_name} profile in AWS config", fg='green')
        except Exception as e:
            logger.warn(f"Error reading AWS config: {e}")
            aws_profile_name = None
    else:
        logger.warn(f"AWS config file {aws_config_path} does not exist")
        aws_profile_name = None

    return aws_profile_name


def get_aws_session(profile_name: Optional[str] = None, region: str = None) -> boto3.Session:
    """
    Get or create an AWS session with proper configuration.
    
    Args:
        profile_name: AWS profile name to use
        region: AWS region name
        
    Returns:
        boto3.Session: Configured AWS session
    """
    if region is None:
        region = region_name
        
    if profile_name is None:
        profile_name = get_aws_profile()
    
    cache_key = f"{profile_name}_{region}"
    
    if cache_key in _sessions_cache:
        return _sessions_cache[cache_key]
    
    try:
        if profile_name:
            session = boto3.session.Session(profile_name=profile_name, region_name=region)
            logger.info(f"Created AWS session with profile: {profile_name}")
        else:
            session = boto3.session.Session(region_name=region)
            logger.info("Using default AWS session")
        
        _sessions_cache[cache_key] = session
        return session
        
    except Exception as e:
        logger.warn(f"Failed to create session with profile {profile_name}: {e}")
        session = boto3.session.Session(region_name=region)
        _sessions_cache[cache_key] = session
        return session


def get_aws_client(service_name: str, 
                  profile_name: Optional[str] = None, 
                  region: str = None,
                  endpoint_url: Optional[str] = None,
                  config: Optional[Config] = None,
                  **kwargs) -> Any:
    """
    Get or create an AWS client with proper configuration.
    
    Args:
        service_name: AWS service name (e.g., 's3', 'secretsmanager', 'ses')
        profile_name: AWS profile name to use
        region: AWS region name
        endpoint_url: Custom endpoint URL for local testing
        config: Botocore configuration
        **kwargs: Additional client configuration
        
    Returns:
        AWS client instance
    """
    if region is None:
        region = region_name
        
    if profile_name is None:
        profile_name = get_aws_profile()
    
    # Create cache key
    cache_key = f"{service_name}_{profile_name}_{region}_{endpoint_url or 'default'}"
    
    if cache_key in _clients_cache:
        return _clients_cache[cache_key]
    
    try:
        # Prepare client configuration
        client_config = {
            'service_name': service_name,
            'region_name': region,
            **kwargs
        }
        
        if endpoint_url:
            client_config['endpoint_url'] = endpoint_url
            
        if config:
            client_config['config'] = config
        elif service_name == 's3':
            client_config['config'] = my_config
        
        # Create session and client
        session = get_aws_session(profile_name, region)
        client = session.client(**client_config)
        
        _clients_cache[cache_key] = client
        logger.debug(f"Created {service_name} client for region {region}")
        return client
        
    except Exception as e:
        logger.error(f"Failed to create {service_name} client: {e}")
        raise


def get_s3_client(profile_name: Optional[str] = None, region: str = None, **kwargs) -> Any:
    """
    Get S3 client with standard configuration.
    
    Args:
        profile_name: AWS profile name to use
        region: AWS region name
        **kwargs: Additional client configuration
        
    Returns:
        boto3 S3 client
    """
    return get_aws_client('s3', profile_name=profile_name, region=region, **kwargs)


def get_secrets_manager_client(profile_name: Optional[str] = None, region: str = None, **kwargs) -> Any:
    """
    Get Secrets Manager client.
    
    Args:
        profile_name: AWS profile name to use
        region: AWS region name
        **kwargs: Additional client configuration
        
    Returns:
        boto3 Secrets Manager client
    """
    return get_aws_client('secretsmanager', profile_name=profile_name, region=region, **kwargs)


def get_ses_client(profile_name: Optional[str] = None, region: str = None, **kwargs) -> Any:
    """
    Get SES client.
    
    Args:
        profile_name: AWS profile name to use
        region: AWS region name
        **kwargs: Additional client configuration
        
    Returns:
        boto3 SES client
    """
    return get_aws_client('ses', profile_name=profile_name, region=region, **kwargs)


def get_lambda_client(profile_name: Optional[str] = None, region: str = None, **kwargs) -> Any:
    """
    Get Lambda client.
    
    Args:
        profile_name: AWS profile name to use
        region: AWS region name
        **kwargs: Additional client configuration
        
    Returns:
        boto3 Lambda client
    """
    return get_aws_client('lambda', profile_name=profile_name, region=region, **kwargs)


def get_sns_client(profile_name: Optional[str] = None, region: str = None, endpoint_url: Optional[str] = None, **kwargs) -> Any:
    """
    Get SNS client.
    
    Args:
        profile_name: AWS profile name to use
        region: AWS region name
        endpoint_url: Custom endpoint URL for local testing
        **kwargs: Additional client configuration
        
    Returns:
        boto3 SNS client
    """
    return get_aws_client('sns', profile_name=profile_name, region=region, endpoint_url=endpoint_url, **kwargs)


def get_sqs_client(profile_name: Optional[str] = None, region: str = None, endpoint_url: Optional[str] = None, **kwargs) -> Any:
    """
    Get SQS client.
    
    Args:
        profile_name: AWS profile name to use
        region: AWS region name
        endpoint_url: Custom endpoint URL for local testing
        **kwargs: Additional client configuration
        
    Returns:
        boto3 SQS client
    """
    return get_aws_client('sqs', profile_name=profile_name, region=region, endpoint_url=endpoint_url, **kwargs)


def get_aws_credentials_from_file() -> Optional[Dict[str, str]]:
    """
    Get AWS credentials from local config file if available.
    
    Returns:
        dict: AWS credentials or None if not found
    """
    config_file = os.path.join(envdir, "aws_config.json")
    
    if os.path.exists(config_file):
        try:
            with open(config_file) as f:
                return json.load(f)
        except Exception as e:
            logger.warn(f"Failed to read AWS config file: {e}")
    
    return None


def clear_cache():
    """Clear all cached clients and sessions."""
    global _clients_cache, _sessions_cache
    _clients_cache.clear()
    _sessions_cache.clear()
    logger.info("Cleared AWS clients and sessions cache")


# Legacy compatibility functions for existing code
def init_aws_session() -> Any:
    """
    Legacy function for backward compatibility.
    Returns a Secrets Manager client.
    """
    return get_secrets_manager_client()


# Environment-based client creation for backward compatibility
def create_boto3_kwargs() -> Dict[str, Any]:
    """
    Create boto3 kwargs from environment variables.
    
    Returns:
        dict: boto3 configuration kwargs
    """
    boto3kwargs = {"region_name": region_name}
    
    if os.getenv("AWS_ACCESS_KEY", "") != "" and os.getenv("AWS_SECRET_KEY", "") != "":
        boto3kwargs["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY")
        boto3kwargs["aws_secret_access_key"] = os.getenv("AWS_SECRET_KEY")
    
    return boto3kwargs
