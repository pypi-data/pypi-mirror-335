from time import sleep

from boto3 import Session
from botocore.exceptions import ClientError
from sagemaker_studio_analytics_extension.utils.exceptions import (
    InvalidEMRServerlessApplicationStateError,
    EMRServerlessApplicationStartTimeoutFault,
    EMRServerlessFault,
    EMRServerlessError,
)
from sagemaker_studio_analytics_extension.utils.region_utils import (
    get_regional_dns_suffix,
)

# Maximum wait time would be 150s
MAX_NUMBER_OF_RETRIES = 5
DEFAULT_WAIT_TIME_BETWEEN_RETRIES = 30
ERROR = "Error"
MESSAGE = "Message"
CODE = "Code"


class EMRServerlessApplication:
    def __init__(self, session: Session, application_id: str):
        self.session = session
        self.client = session.client("emr-serverless")
        self.application_id = application_id

    def start_application(self):
        try:
            self.client.start_application(applicationId=self.application_id)
        except ClientError as e:
            if e.response[ERROR][CODE] in [
                "ResourceNotFoundException",
                "ValidationException",
                "ServiceQuotaExceededException",
            ]:
                raise EMRServerlessError(e.response[ERROR][MESSAGE]) from e
            raise EMRServerlessFault(
                "Exception when starting EMR Serverless Application"
            ) from e
        except Exception as e:
            raise EMRServerlessFault(
                "Exception when starting EMR Serverless Application"
            ) from e

    def get_application(self):
        try:
            response = self.client.get_application(applicationId=self.application_id)
        except ClientError as e:
            if e.response[ERROR][CODE] in [
                "ResourceNotFoundException",
                "ValidationException",
            ]:
                raise EMRServerlessError(e.response[ERROR][MESSAGE]) from e
            raise EMRServerlessFault(
                "Exception when getting EMR Serverless Application details"
            ) from e
        except Exception as e:
            raise EMRServerlessFault(
                "Exception when getting EMR Serverless Application details"
            ) from e
        return response

    def poll_until_required_application_state(
        self,
        required_state: str,
        retryable_states: list[str],
        max_tries: int = MAX_NUMBER_OF_RETRIES,
        wait_time_in_seconds: int = DEFAULT_WAIT_TIME_BETWEEN_RETRIES,
    ):
        retry_number = 0
        while retry_number < max_tries:
            application_state = self.get_application().get("application").get("state")
            if application_state == required_state:
                return True
            elif application_state in retryable_states:
                print(
                    f"Waiting for EMR Serverless application state to become {required_state}"
                )
                sleep(wait_time_in_seconds)
                retry_number += 1
            else:
                raise InvalidEMRServerlessApplicationStateError(
                    f"Application state {application_state} of "
                    f"application {self.application_id} is invalid "
                )

        # Fault because dependent service EMR Serverless is taking too long to start
        raise EMRServerlessApplicationStartTimeoutFault(
            f"State of application {self.application_id} is not {required_state} "
            f"Please retry after 60 seconds "
        )

    def get_livy_endpoint(self):
        # Livy endpoint urls are not returned by EMR Serverless and must be constructed in the format
        # https://<application_id>.livy.emr-serverless-services.<region>.amazonaws.com

        region = self.session.region_name
        dns_suffix = get_regional_dns_suffix(self.session._session, region)
        return f"https://{self.application_id}.livy.emr-serverless-services.{region}.{dns_suffix}"
