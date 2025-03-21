import boto3
from botocore.exceptions import ClientError
import json

class SecretManager:

    def __init__(self, secret_name, region_name):
        self.secret_name = secret_name
        self._cached_secrets = None
        self._region_name = region_name

    def fetch_secrets(self):
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=self._region_name
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=self.secret_name
            )
        except ClientError as e:
            raise e

        secret = get_secret_value_response['SecretString']
        return json.loads(secret)

    def load_secrets(self):
        if self._cached_secrets is None:
            self._cached_secrets = self.fetch_secrets()
        return self._cached_secrets