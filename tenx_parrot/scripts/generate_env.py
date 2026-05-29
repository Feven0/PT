"""Environment configuration generator with AWS Secrets Manager integration."""
import os
import json
import boto3
import tempfile
import argparse
from pathlib import Path
from typing import Dict, Optional
from botocore.exceptions import ClientError

from core.logging import BackendLogger


# Initialize logger
logger = BackendLogger(
    name="config",
    level="DEBUG",
    colors={
        "config": "bright_magenta",
        "aws": "bright_cyan",
        "env": "bright_blue",
        "error": "bright_red"
    }
).get_logger()

def get_aws_profile(region: str = "us-east-1") -> str:
    """Get AWS profile command line arguments."""
    profile_exists = False
    aws_config = Path.home() / ".aws" / "config"
    
    if aws_config.exists():
        with aws_config.open() as f:
            profile_exists = "tenac" in f.read()
    
    if profile_exists:
        profile_name = os.getenv("AWS_PROFILE", "tenac")
        return f"--profile {profile_name} --region {region}"
    
    return f"--region {region}"


def get_ssm_secret(secret_id: str, profile: str) -> str:
    """Get secret from AWS Secrets Manager."""
    try:
        # Parse profile string
        profile_parts = profile.split()
        profile_name = None
        region = "us-east-1"
        
        for i, part in enumerate(profile_parts):
            if part == "--profile":
                profile_name = profile_parts[i + 1]
            elif part == "--region":
                region = profile_parts[i + 1]
        
        # Create session
        session = boto3.Session(profile_name=profile_name, region_name=region)
        client = session.client('secretsmanager')
        
        # Get secret
        response = client.get_secret_value(SecretId=secret_id)
        if "SecretString" in response:
            return response["SecretString"]
        return ""
        
    except ClientError as e:
        logger.error(f"Failed to get secret {secret_id}: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error getting secret: {e}")
        return ""


def generate_api_key(secret_id: str, env: str = "dev", key: str = "API_KEY") -> str:
    """Generate and save API key."""
    try:
        # Get AWS profile
        profile = get_aws_profile()
        
        # Check existing key
        existing_key = get_ssm_secret(secret_id, profile)
        
        if existing_key:
            return existing_key
        
        # Generate new key
        session = boto3.Session()
        client = session.client('secretsmanager')
        
        response = client.get_random_password(
            PasswordLength=20,
            ExcludePunctuation=True
        )
        new_key = response["RandomPassword"]
        
        # Save new key
        key_json = {key: new_key}
        client.create_secret(
            Name=secret_id,
            SecretString=json.dumps(key_json)
        )
        
        return json.dumps(key_json)
        
    except Exception as e:
        logger.error(f"Failed to generate API key: {e}")
        return ""


class EnvGenerator:
    """Environment configuration generator."""
    
    def __init__(self,
                 stage: str = "dev", 
                 strapi_stage: str = "dev",
                 secret_name: str = "tenx/env/vars",
                 aws_region: str = "us-east-1",
                 aws_profile: str = "tenac"):
        """Initialize generator.
        
        Args:
            stage: Environment stage (dev, staging, prod)
        """
        self.stage = stage.lower()
        self.strapi_stage = strapi_stage.lower()
        # get the env file name
        self.stage_env_file = Path(f".env.{self.stage}")
        self.env_file = Path(f".env")

        #
        self.secret_name = secret_name
        
        #
        self.aws_region = aws_region
        self.aws_profile = aws_profile
        
        # Log initialization
        logger.debug(
            "env_generator_init",
            context="config",
            json_data={
                "Configuration": {
                    "Stage": self.stage,
                    "Env File": str(self.env_file),
                    "Stage Env File": str(self.stage_env_file),
                    "AWS Region": self.aws_region,
                    "AWS Profile": self.aws_profile
                }
            }
        )
    

    def _load_env_file(self) -> Dict[str, str]:
        """Load environment file as dictionary.
        
        Returns:
            Dictionary of environment variables
        """
        try:
            if not self.stage_env_file.exists():
                logger.warning(
                    "stage_env_file_not_found",
                    context="env",
                    file=str(self.stage_env_file)
                )
                return {}
            
            content = self.stage_env_file.read_text()
            env_vars = {}
            
            for line in content.splitlines():
                # Skip comments and empty lines
                if line.startswith('#') or not line.strip():
                    continue
                    
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
            
            
            return env_vars
            
        except Exception as e:
            logger.error(
                "stage_env_file_load_failed",
                context="error",
                error=str(e)
            )
            return {}


    def _get_aws_secret(self, secret_name: str="") -> Optional[Dict]:
        """Get secret from AWS Secrets Manager.
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            Secret data if found, None otherwise
        """
        try:
            if not secret_name:
                secret_name = self.secret_name
            
            cache_filename = f"{secret_name.replace('/', '_')}.json"
            if os.getenv("AWS_PROFILE", "tenac") == "tenac":
                cache_path = Path(f".envdir") / cache_filename
                cache_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                cache_path = Path(tempfile.gettempdir()) / cache_filename

        
            # Try to read from cache first
            if cache_path.exists():
                try:
                    with open(cache_path, 'r') as f:
                        logger.debug(
                            "using cached secret",
                            context="aws",
                            secret=secret_name
                        )
                        return json.load(f)
                except json.JSONDecodeError:
                    cache_path.unlink()  # Delete invalid cache file
            
            # Get Secret from AWS Secrets Manager
            profile = get_aws_profile()
            
            # Get environment variables from AWS
            env_vars = get_ssm_secret(secret_name, profile)

            # Parse secret data
            try:
                secret_data = json.loads(env_vars)
                # Cache the secret
                with open(cache_path, 'w') as f:
                    json.dump(secret_data, f)

                return secret_data               
            except json.JSONDecodeError:
                logger.warning(
                    "secret not found",
                    context="aws",
                    secret=secret_name
                )
                return None
            
        except ClientError as e:
            logger.error(
                f"Error retrieving secret: {e}",
                secret=secret_name
            )
            return None
    
    def _generate_env_content(self) -> str:
        """Generate environment file content.
        
        Returns:
            Environment file content
        """
        
        # Get stage secrets
        stage_secrets = self._load_env_file() or {}
        
        # Get secrets from AWS
        aws_secrets = self._get_aws_secret() or {}

        # Merge secrets
        secrets = {**stage_secrets, **aws_secrets}
        
        # Base configuration
        env_vars = {
            # Stage and Debug
            "STAGE": self.stage,
            "DEBUG": str(self.stage == "dev").lower(),
            
            # LLM Configuration
            "OPENAI_API_KEY": secrets.get("OPENAI_API_KEY", ""),
            "LLM_PROVIDER": "openai",
            "LLM_MODEL": "gpt-4o-mini",
            "LLM_TEMPERATURE": "0.7",
            "LLM_MAX_TOKENS": "2000",
            "LLM_STREAMING": "true",
            
            # Assembly AI
            "ASSEMBLY_AI_KEY": secrets.get("ASSEMBLY_AI_KEY", ""),
            "ASSEMBLY_AI_STREAMING": "true",
            
            # Strapi CMS
            "STRAPI_API_URL": secrets.get("STRAPI_API_URL", ""),
            "STRAPI_AUTH_TOKEN": secrets.get("STRAPI_AUTH_TOKEN", ""),
            "STRAPI_STAGE": self.strapi_stage,
            
            # WebSocket
            "WS_ENABLED": "true",
            "WS_PING_INTERVAL": "25",
            "WS_PING_TIMEOUT": "120",
            "WS_MAX_LIFETIME": "7200",
            
            # WebRTC
            "WEBRTC_ICE_SERVERS": json.dumps([
                {"urls": "stun:stun.l.google.com:19302"},
                {"urls": "stun:stun1.l.google.com:19302"}
            ]),
            
            # Database
            "DATABASE_URL": secrets.get("DATABASE_URL", ""),
            "DATABASE_SCHEMA": "schema.prisma",
            
            # CORS
            "CORS_ORIGINS": json.dumps([
                "http://frog.10academy.org",
                "https://leap.10academy.org",
                f"https://{self.stage}-leap.10academy.org",
                "http://localhost",
                "http://localhost:5500",
                "http://localhost:5000"
            ]),
            "CORS_CREDENTIALS": "true",
            "CORS_METHODS": "*",
            "CORS_HEADERS": "*",
            
            # Server
            "SERVER_HOST": "0.0.0.0",
            "SERVER_PORT": "9900",
            "SERVER_WORKERS": "4",
            "SERVER_RELOAD": str(self.stage == "dev").lower(),
            
            # Email Notifications
            "EMAIL_NOTIFICATIONS_ENABLED": "false",
            "EMAIL_SENDER": secrets.get("EMAIL_SENDER", ""),
            "EMAIL_RECIPIENTS": ",".join(secrets.get("EMAIL_RECIPIENTS", [])),
            "SMTP_HOST": secrets.get("SMTP_HOST", ""),
            "SMTP_PORT": secrets.get("SMTP_PORT", "587"),
            "SMTP_USER": secrets.get("SMTP_USER", ""),
            "SMTP_PASS": secrets.get("SMTP_PASS", ""),
            "SMTP_USE_TLS": "true",
            
            # Slack Notifications
            "SLACK_NOTIFICATIONS_ENABLED": "false",
            "SLACK_WEBHOOK_URL": secrets.get("SLACK_WEBHOOK_URL", ""),
            
            # Storage Configuration
            "PRIMARY_STORAGE": "strapi",
            "SYNC_STORAGES": "false",
            "STRAPI_ENABLED": "true",
            "WEAVIATE_ENABLED": "false",
            "STRAPI_URL": secrets.get("STRAPI_URL", ""),
            "STRAPI_TOKEN": secrets.get("STRAPI_AUTH_TOKEN", ""),
            "WEAVIATE_URL": secrets.get("WEAVIATE_URL", ""),
            "WEAVIATE_API_KEY": secrets.get("WEAVIATE_API_KEY", ""),
            
            # Queue Configuration
            "QUEUE_ENABLED": "false",
            "QUEUE_MIN_WORKERS": "1",
            "QUEUE_MAX_WORKERS": "5",
            "QUEUE_URL": "",
            
            # Cache Configuration
            "CACHE_ENABLED": "false",
            "CACHE_URL": "redis://localhost:6379",
            "CACHE_MAX_MEMORY_MB": "512"
        }
        
        # Generate content
        content = "# Generated environment configuration\n"
        content += f"# Stage: {self.stage}\n\n"
        
        for key, value in sorted(env_vars.items()):
            content += f"{key}={value}\n"
        
        return content
    
    def generate(self) -> None:
        """Generate environment file."""
        try:
            # Generate content
            content = self._generate_env_content()
            
            # Write to file
            self.env_file.write_text(content)
                        
        except Exception as e:
            logger.error(
                "env_generation_failed",
                context="error",
                error=str(e)
            )
            raise
    
if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser(description="Set up environment")
    parser.add_argument(
        "--stage",
        default="dev",
        choices=["dev", "test", "prod"],
        help="Environment to set up"
    )
    args = parser.parse_args()
    
    generator = EnvGenerator(args.stage)
    generator.generate()

