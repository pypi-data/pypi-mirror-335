import json
import time

from moonshotai_integration.utils.utils import is_file_exists, compress_csv, get_current_timestamp
from moonshotai_integration.utils.exceptions import IntegrationError, ErrorType
from moonshotai_integration.utils.response import Response
from moonshotai_integration.utils.consts import *
from typing import Optional, Dict, Any, Union
from botocore.exceptions import ClientError
from enum import Enum
import pandas as pd
import datetime
import requests
import boto3
import os


class DatasetType(str, Enum):
    TRANSACTIONS = "transactions"
    GAME_SESSIONS = "game_sessions"
    USERS = "users"

    @property
    def col_name(self):
        mapping = {
            DatasetType.TRANSACTIONS: "action_date",
            DatasetType.GAME_SESSIONS: "action_date",
            DatasetType.USERS: "lead_date",
        }
        return mapping[self]


class DataIntegrationClient:
    def __init__(
            self,
            company: str,
            token: str
    ):
        """
        Initialize the Data Integration client.

        Args:
            company: The company name
            token: Authentication token provided by the client

        Raises:
            ValueError: If dataset_type is invalid or dates are in wrong format
        """

        if company == '' or company is None:
            raise ValueError("Company must be provided")
        self.company = company

        if token == '' or token is None:
            raise ValueError("Token must be provided")
        self.token = token

        self.file_path = None
        self.start_date = None
        self.end_date = None
        self.dataset_type = None

        self._api_base_url = 'https://8fw1x8an4a.execute-api.eu-west-2.amazonaws.com/api/prod'
        self._s3_bucket = f'{self.company}-storage-bucket'
        self._s3_base_path = 'data_integration/temp'

        self._aws_credentials: Optional[Dict[str, str]] = None
        self._s3_client: Optional[Any] = None
        self._compressed_file_path = None
        self._temp_s3_key = None
        self._response = None

    def _set_params(self, file_path, start_date, end_date, dataset_type):
        is_file_exists(file_path)
        self.file_path = file_path

        if isinstance(dataset_type, str):
            try:
                self.dataset_type = DatasetType(dataset_type.lower())
            except ValueError:
                raise ValueError(
                    f"Invalid dataset_type. Must be one of: {', '.join([t.value for t in DatasetType])}"
                )
        else:
            self.dataset_type = dataset_type

        try:
            self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            self.end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Dates must be in YYYY-MM-DD format")

        if self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")

    def _get_aws_credentials(self) -> Dict[str, str]:
        """Fetch AWS credentials from the credentials API."""
        endpoint = f"{self._api_base_url}/get_credentials"
        response = None

        headers = {
            "Content-Type": "application/json",
            "api-key": self.token,
            "company": self.company
        }

        params = {"company": self.company}

        try:
            response = requests.get(endpoint, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            msg = f"Failed to retrieve credentials"
            if response is not None and response.status_code == 500:
                msg = ("Could not initiate client, your account may be disabled. Please contact support for "
                       "assistance.")
            raise IntegrationError(ErrorType.INTEGRATION_ERROR, msg)

    def _initialize_s3_client(self) -> boto3:
        """Initialize S3 client with the fetched credentials."""
        return boto3.client(
            's3',
            aws_access_key_id=self._aws_credentials['aws_access_key_id'],
            aws_secret_access_key=self._aws_credentials['aws_secret_access_key']
        )

    def _validate_dates_in_dataset(self, df: pd.DataFrame, date_column: str) -> bool:
        """
        Validate that all dates in the dataset are within the specified range.

        Args:
            df: Pandas DataFrame containing the dataset
            date_column: Name of the date column to validate

        Returns:
            bool: True if all dates are valid

        Raises:
            ValueError: If dates are outside the valid range
        """
        tmp_date_col = 'tmp_date_col'
        df[tmp_date_col] = pd.to_datetime(df[date_column]).dt.date
        invalid_dates = df[
            (df[tmp_date_col] < self.start_date) |
            (df[tmp_date_col] > self.end_date)
            ]

        if not invalid_dates.empty:
            msg = f"Found {len(invalid_dates)} rows with dates outside the valid range ({self.start_date} to {self.end_date})"
            raise IntegrationError(ErrorType.INTEGRATION_ERROR, msg)

        del df[tmp_date_col]
        return True

    def _trigger_data_validation(self, s3_key: str) -> Dict[str, Any]:
        """
        Trigger the data validation API.

        Args:
            s3_key: S3 path to the uploaded dataset

        Returns:
            Dict containing validation results
        """
        endpoint = f"{self._api_base_url}/validate"
        response = None

        headers = {
            "Content-Type": "application/json",
            "api-key": self.token,
            "company": self.company
        }

        payload = {
            "company": self.company,
            "bucket": self._s3_bucket,
            "key": s3_key,
            "fileType": self.dataset_type.value,
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            resp = response.json()
            err_msg = resp.get("error", "an error occurred")
            msg = f"Data validation failed: {err_msg}"
            if response is not None and response.status_code == 500:
                msg = ("Could not run data validation, your account may be disabled. Please contact support for "
                       "assistance.")
            raise IntegrationError(ErrorType.VALIDATION_ERROR, msg)

    def _read_csv(self) -> pd.DataFrame:
        """
        Read a CSV file into a Pandas DataFrame.

        Returns:
            pd.DataFrame: The loaded DataFrame
        """
        return pd.read_csv(self.file_path, dtype=str)

    def _process_csv_by_date(self, s3_key):
        """
        Trigger the data partitioning by date API.

        Args:
            s3_key: S3 path to the uploaded dataset
        """
        endpoint = f"{self._api_base_url}/process_data"
        response = None

        headers = {
            "Content-Type": "application/json",
            "api-key": self.token,
            "company": self.company
        }

        payload = {
            "company": self.company,
            "bucket": self._s3_bucket,
            "file_path": s3_key,
            "dataset_type": self.dataset_type.value,
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            resp = response.json()
            err_msg = resp.get("error", "an error occurred")
            msg = f"Data processing failed: {err_msg}"
            if response is not None and response.status_code == 500:
                msg = ("Could not process your data, your account may be disabled. Please contact support for "
                       "assistance.")
            elif response is not None and response.status_code == 504:
                msg = "Your request has timed out due to processing a large dataset. Please try again with a smaller dataset and reducing the date range."
            raise IntegrationError(ErrorType.PROCESS_ERROR, msg)

    def _check_status(self, path: str, tracking_id: str):
        """
        Trigger the status check API.

        Args:
            path: S3 path where status is located
            tracking_id: Tracking ID for the process
        """
        endpoint = f"{self._api_base_url}/check_status"
        response = None

        headers = {
            "Content-Type": "application/json",
            "api-key": self.token,
            "company": self.company
        }

        payload = {
            "company": self.company,
            "bucket": self._s3_bucket,
            "type": path,
            "tracking_id": tracking_id
        }

        for idx in range(1, MAX_TRIES):
            try:
                response = requests.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                resp_dict = response.json()
                status = resp_dict.get('status')
                if status == QUEUING and idx > 1:
                    msg = "Was not able to process request. Please contact support for assistance."
                    raise IntegrationError(ErrorType.PROCESS_ERROR, msg)

                if status in (PENDING, QUEUING):
                    time.sleep(SLEEP_TIME)
                    continue

                if status in (SUCCESS, FAILED):
                    return resp_dict

            except requests.exceptions.RequestException as e:
                msg = f"Data processing failed"
                if response is not None and response.status_code == 500:
                    msg = (
                        "Could not check the process status, your account may be disabled. Please contact support for "
                        "assistance.")

                elif response is not None and response.status_code == 504:
                    msg = "Your request has timed out due to processing a large dataset. Please try again with a smaller dataset and reducing the date range."

                raise IntegrationError(ErrorType.PROCESS_ERROR, msg)

        return None

    def _handle_status_checking(self, path: str, tracking_id: str):
        """
        Trigger the status check API.

        Args:
            path: S3 path where status is located
            tracking_id: Tracking ID for the process

        Returns: Dict containing operation results
        """
        status_dict = self._check_status(path, tracking_id)
        if status_dict is None:
            raise IntegrationError(ErrorType.INTEGRATION_ERROR, "Failed to retrieve status")

        is_success = status_dict['success']
        if not is_success:
            msg = f"Processing failed: {status_dict['message']}"
            raise IntegrationError(ErrorType.VALIDATION_ERROR, msg)

        return status_dict

    def _process_and_upload_dataset(self, file_path: str, dataset_type: Union[DatasetType, str], start_date: str,
                                    end_date: str):
        self._response = Response()
        self._set_params(file_path=file_path, start_date=start_date, end_date=end_date, dataset_type=dataset_type)
        self._aws_credentials = self._get_aws_credentials()
        self._s3_client = self._initialize_s3_client()
        df = self._read_csv()

        # Date column validation
        date_column = self.dataset_type.col_name
        self._validate_dates_in_dataset(df, date_column)

        # Upload to temporary S3 location
        timestamp = get_current_timestamp()
        file_name = os.path.basename(self.file_path)
        self._temp_s3_key = f"{self._s3_base_path}/{self.dataset_type.value}/{timestamp}_{file_name}.gz"

        try:
            # Upload file to S3
            self._compressed_file_path = f"{self.file_path}.gz"
            compress_csv(self.file_path, self._compressed_file_path)
            self._s3_client.upload_file(
                self._compressed_file_path,
                self._s3_bucket,
                self._temp_s3_key,
                ExtraArgs={
                    "ContentType": "text/csv",
                    "ContentEncoding": "gzip"
                }
            )
        except ClientError as e:
            msg = f"Failed to upload files. You might not have the required permissions."
            raise IntegrationError(ErrorType.INTEGRATION_ERROR, msg)

    def _handle_data_validation(self):
        validation_resp = self._trigger_data_validation(self._temp_s3_key)
        validation_tracking_id = validation_resp.get("tracking_id")
        if validation_tracking_id is None:
            raise IntegrationError(ErrorType.INTEGRATION_ERROR, "Failed to retrieve tracking ID for validation")

        status_dict = self._handle_status_checking(VALIDATION_STATUS, validation_tracking_id)
        val_result_str = status_dict.get('validation_results')
        if val_result_str is None:
            raise IntegrationError(ErrorType.VALIDATION_ERROR, "Failed to retrieve validation results")

        validation_result = json.loads(val_result_str)
        for err_type, err_list in validation_result.items():
            if err_type != 'datasetName' and len(err_list) > 0:
                msg = "Data validation failed with errors"
                raise IntegrationError(ErrorType.VALIDATION_ERROR, msg, validation_result)

    def _handle_data_processing(self):
        process_resp = self._process_csv_by_date(self._temp_s3_key)
        process_tracking_id = process_resp.get("tracking_id")
        if process_tracking_id is None:
            raise IntegrationError(ErrorType.INTEGRATION_ERROR, "Failed to retrieve tracking ID for processing")

        status_dict = self._handle_status_checking(PROCESS_STATUS, process_tracking_id)

    def upload_data(self, file_path: str, dataset_type: Union[DatasetType, str], start_date: str, end_date: str):
        """
        Main method to process a dataset.
        Args:
            file_path: Local file path of the dataset (e.g., path/to/your/file.csv)
            dataset_type: Type of dataset to upload (transactions, game_sessions, users)
            start_date: Start date for filtering the dataset (YYYY-MM-DD)
            end_date: End date for filtering the dataset (YYYY-MM-DD)

        Returns:
            Dict containing operation results
        """
        try:
            self._process_and_upload_dataset(file_path, dataset_type, start_date, end_date)
            self._handle_data_validation()
            self._handle_data_processing()

        except IntegrationError as e:
            self._response.set_message(str(e))
            self._response.set_errors(e.errors)
            return self._response
        except ValueError as e:
            self._response.set_message(str(e))
            return self._response

        finally:
            if self._compressed_file_path is not None and os.path.exists(self._compressed_file_path):
                os.remove(self._compressed_file_path)

        self._response.set_success_status(True)
        self._response.set_message("Data uploaded successfully")
        return self._response

    def validate_data(self, file_path: str, dataset_type: Union[DatasetType, str], start_date: str, end_date: str):
        """
        Main method to validate a dataset.
        Args:
            file_path: Local file path of the dataset (e.g., path/to/your/file.csv)
            dataset_type: Type of dataset to upload (transactions, game_sessions, users)
            start_date: Start date for filtering the dataset (YYYY-MM-DD)
            end_date: End date for filtering the dataset (YYYY-MM-DD)

        Returns:
            Dict containing operation results
        """
        try:
            self._process_and_upload_dataset(file_path, dataset_type, start_date, end_date)
            self._handle_data_validation()

        except IntegrationError as e:
            self._response.set_message(str(e))
            self._response.set_errors(e.errors)
            return self._response
        except ValueError as e:
            self._response.set_message(str(e))
            return self._response

        finally:
            if self._compressed_file_path is not None and os.path.exists(self._compressed_file_path):
                os.remove(self._compressed_file_path)

        self._response.set_success_status(True)
        self._response.set_message("Data validation completed successfully")
        return self._response
