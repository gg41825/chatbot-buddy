import configparser
import os

config = configparser.ConfigParser()
config.allow_no_value = True
config.read('service.conf')

# Support environment variables for Cloud Run deployment
# This allows using Secret Manager or environment variables instead of service.conf
def get_config_value(section, key, fallback=None):
    """
    Get configuration value from environment variable first, then fall back to config file.
    Environment variable format: SECTION_KEY (e.g., MYSQL_HOST, MYSQL_PORT)
    """
    env_key = f"{section.upper()}_{key.upper().replace('.', '_')}"
    env_value = os.getenv(env_key)

    if env_value is not None:
        return env_value

    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return fallback
