import os
from typing import Dict, Optional

class AstrafyTrainingEnvironment:
    """
    A class to manage environment-specific configurations for project, dataset, and service account.
    Allows overriding default values via constructor parameters.
    """

    def __init__(self, environment: str = None, configs: Optional[Dict[str, Dict[str, str]]] = None):
        """
        Initializes the AstrafyTrainingEnvironment with the given environment and optional overrides for project, dataset, and service account.
        If no environment is provided, it attempts to determine it from the OS environment variable 'ENVIRONMENT'.

        Args:
            environment (str, optional): The environment (e.g., 'dev', 'prd'). Defaults to None.
            configs (Dict[str, Dict[str, str]], optional): A dictionary containing environment-specific configurations. Defaults to None.
        """
        self.environment = environment or os.getenv('ENVIRONMENT')
        if not self.environment:
            raise ValueError("Environment not specified. Please provide an environment or set the 'ENVIRONMENT' environment variable.")

        self.config = self._load_config(configs)


    def _load_config(self, configs: Optional[Dict[str, Dict[str, str]]] = None) -> Dict:
        """
        Loads the configuration based on the environment, using provided configs if available.

        Returns:
            Dict: A dictionary containing the configuration for the specified environment.

        Raises:
            ValueError: If the environment is not supported.
        """
        # Define default configurations for different environments
        default_config = {
            "dev": {
                "project": "dev-project-id",
                "dataset": "dev_dataset",
                "service_account": "dev-service-account@dev-project-id.iam.gserviceaccount.com"
            },
            "prd": {
                "project": "prd-project-id",
                "dataset": "prd_dataset",
                "service_account": "prd-service-account@prd-project-id.iam.gserviceaccount.com"
            }
        }

        if configs and self.environment in configs:
            # Merge the provided configs with the default configs
            config = default_config.get(self.environment, {}).copy()  # Start with a copy of the default config
            config.update(configs[self.environment])  # Update with values from configs
        else:
            config = default_config.get(self.environment, {})

        if not config:
            raise ValueError(f"Unsupported environment: {self.environment}. Supported environments are: {', '.join(default_config.keys())}")

        return config

    def get_project(self) -> str:
        """
        Returns the project ID for the current environment.

        Returns:
            str: The project ID.
        """
        return self.config["project"]

    def get_dataset(self) -> str:
        """
        Returns the dataset ID for the current environment.

        Returns:
            str: The dataset ID.
        """
        return self.config["dataset"]

    def get_service_account(self) -> str:
        """
        Returns the service account for the current environment.

        Returns:
            str: The service account for the current environment.
        """
        return self.config["service_account"]

