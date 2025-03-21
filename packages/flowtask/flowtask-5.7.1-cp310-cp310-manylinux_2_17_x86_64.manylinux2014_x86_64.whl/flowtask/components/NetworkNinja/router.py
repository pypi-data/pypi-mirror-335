from collections.abc import Callable
import asyncio
import logging
from datetime import datetime, timezone
import time
from typing import Union
import pandas as pd
import backoff
from datamodel import BaseModel
from datamodel.parsers.json import json_encoder, json_decoder
from datamodel.exceptions import ValidationError
from querysource.interfaces.databases.mongo import DocumentDB
from querysource.conf import async_default_dsn
from querysource.outputs.tables import PgOutput
from ...exceptions import (
    ComponentError,
    DataError,
    ConfigError,
    DataNotFound
)
from ...components import FlowComponent
from ...interfaces.http import HTTPService
from ...conf import (
    NETWORKNINJA_API_KEY,
    NETWORKNINJA_BASE_URL,
    NETWORKNINJA_ENV
)
from .models import NetworkNinja_Map, NN_Order


logging.getLogger('pymongo.connection').setLevel(logging.INFO)
logging.getLogger('pymongo.topology').setLevel(logging.INFO)

class NetworkNinja(HTTPService, FlowComponent):
    """
    NetworkNinja.

        Overview: Router for processing NetworkNinja Payloads.

    Properties:
        +---------------+----------+------------------------------------------+
        | Name          | Required | Description                              |
        +---------------+----------+------------------------------------------+
        | action        | Yes      | Type of operation (get_batch, etc)      |
        +---------------+----------+------------------------------------------+
        | credentials   | No       | API credentials (taken from config)      |
        +---------------+----------+------------------------------------------+
        | payload       | No       | Additional payload parameters            |
        +---------------+----------+------------------------------------------+

    Supported Types:
        - get_batch: Retrieves batch acceptance data
    """
    accept: str = 'application/json'

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ) -> None:
        self._action: str = kwargs.pop('action', None)
        self.chunk_size: int = kwargs.get('chunk_size', 100)
        self.use_proxies: bool = kwargs.pop('use_proxies', False)
        self.paid_proxy: bool = kwargs.pop('paid_proxy', False)
        self.base_url = NETWORKNINJA_BASE_URL
        self.avoid_acceptance: bool = kwargs.get('avoid_acceptance', False)
        self.batch_id: str = kwargs.get('batch_id', None)
        super(NetworkNinja, self).__init__(loop=loop, job=job, stat=stat, **kwargs)
        self.semaphore = asyncio.Semaphore(10)  # Adjust the limit as needed
        self._model_caching: dict = kwargs.get('model_cache', {})
        self._result: dict = {}
        self.accept = 'application/json'
        # AWS DocumentDB connection:
        self._document = DocumentDB(use_pandas=False)
        self._pgoutput = PgOutput(dsn=async_default_dsn, use_async=True)

    async def close(self):
        pass

    def _evaluate_input(self):
        if self.previous or self.input is not None:
            self.data = self.input

    def chunkify(self, lst, n):
        """Split list lst into chunks of size n."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    async def start(self, **kwargs):
        self._counter: int = 0
        self._evaluate_input()
        if not self._action:
            raise RuntimeError(
                'NetworkNinja component requires a *action* Function'
            )
        if self._action == 'get_batch':
            # Calling Download Batch from NN Queue.
            # Set up headers with API key
            self.headers.update({
                "X-Api-Key": NETWORKNINJA_API_KEY
            })
            return await super(NetworkNinja, self).start(**kwargs)
        # in other cases, NN requires a previous dataset downloaded.
        if not isinstance(self.data, (dict, list)):
            raise ComponentError(
                "NetworkNinja requires a Dictionary or a List as Payload"
            )
        return True

    async def run(self):
        """Run NetworkNinja Router."""
        tasks = []
        fn = getattr(self, self._action)
        self.add_metric("ACTION", self._action)
        self._result = {}
        if self._action == 'get_batch':
            result = await fn()

            # Check Length of the Payload:
            try:
                num_elements = len(result.get('data', []))
            except TypeError:
                num_elements = 0

            # Add metrics
            self.add_metric("PAYLOAD_LENGTH", num_elements)

            if not result:
                raise DataNotFound(
                    "No data returned from Network Ninja"
                )

            self._result = result
            return self._result
        elif self._action == 'process_payload':
            if isinstance(self.data, dict):
                # Typical NN payload extract data from dictionary:
                tasks = [
                    fn(
                        idx,
                        row,
                    ) for idx, row in enumerate(self.data.get('data', []))
                ]
            elif isinstance(self.data, list):
                tasks = [
                    fn(
                        idx,
                        row,
                    ) for idx, row in enumerate(self.data)
                ]
            elif isinstance(self.data, pd.DataFrame):
                tasks = [
                    fn(
                        idx,
                        row,
                    ) for idx, row in self.data.iterrows()
                ]
            # Execute tasks concurrently
            await self._processing_tasks(tasks)
            # Processing and saving the elements into DB:
            results = []
            for data_type in NN_Order:
                if data_type in self._result:
                    data = self._result[data_type]
                    self._logger.notice(
                        f"Processing Data Type: {data_type}: {len(data)}"
                    )
                    if data:
                        result = await self._saving_payload(
                            data_type, data
                        )
                        results.extend(result)
            if results:
                self._result = pd.concat(results, axis=0, ignore_index=True)
        return self._result

    async def _processing_tasks(self, tasks: list) -> pd.DataFrame:
        """Process tasks concurrently."""
        results = []
        for chunk in self.chunkify(tasks, self.chunk_size):
            result = await asyncio.gather(*chunk, return_exceptions=True)
            if result:
                results.extend(result)
        return results

    @backoff.on_exception(
        backoff.expo,
        (asyncio.TimeoutError),
        max_tries=2
    )
    async def process_payload(
        self,
        idx,
        row
    ):
        async with self.semaphore:
            # Processing first the Metadata:
            metadata = row.get('metadata', {})
            payload = row.get('payload', {})
            # payload_time = metadata.get('timestamp')
            orgid = metadata.get('orgid', None)
            if not orgid:
                orgid = payload.get('orgid', None)
            # Data Type:
            data_type = metadata.get('type', None)
            if not data_type:
                raise DataError(
                    (
                        "NetworkNinja: Data Type not found in Metadata"
                        f" Current Meta: {metadata}"
                    )
                )
            # Creating the Model Instances:
            if data_type not in self._result:
                self._result[data_type] = []
            # Get the Model for the Data Type
            try:
                mdl = NetworkNinja_Map.get(data_type)
            except Exception as e:
                raise DataError(
                    f"NetworkNinja: Model not found for Data Type: {data_type}"
                )
            error = None
            try:
                # First: adding client and org to payload:
                payload['orgid'] = orgid
                # Validate the Data
                data = mdl(**dict(payload))
                self._result[data_type].append(data)
                return data, error
            except ValidationError as e:
                self._logger.warning('Error: ==== ', e)
                error = e.payload
                self._logger.warning(
                    f'Validation Errors: {e.payload}'
                )
                # TODO: save bad payload to DB
                return None, error
            except Exception as e:
                print(f'Error: {e}')
                error = str(e)
                return None, error

    @backoff.on_exception(
        backoff.expo,
        (asyncio.TimeoutError),
        max_tries=2
    )
    async def _saving_payload(
        self,
        data_type: str,
        data: list[dict]
    ):
        """
        Save the Payload into the Database.
        """
        async with self.semaphore:
            # Iterate over all keys in data:
            if not data:
                return
            results = []
            for item in data:
                if data_type == 'form_data':
                    # save the store visited:
                    store = item.store_number
                    store.custom_fields = json_encoder(
                        store.custom_fields
                    )
                    try:
                        await store.on_sync()
                    except Exception as e:
                        self._logger.error(
                            f"Error saving Store: {e}"
                        )
                    try:
                        if item.previous_form_id:
                            # override the existing
                            previous = item.form_id
                            # To preserve previous_form_id
                            item.form_id = item.previous_form_id
                            # swapped:
                            item.current_form_id = previous
                    except Exception as e:
                        self._logger.error(
                            f"Error swapping form_id: {e}"
                        )
                    result = await item.sync(
                        pk=['form_id', 'formid'],
                        table_name='form_data',
                        schema='networkninja'
                    )
                    # result = await self.upsert_record(
                    #     ds,
                    #     pk=['form_id', 'formid'],
                    #     table_name='form_data',
                    #     schema='networkninja'
                    # )
                    if result:
                        # Then, saving this into the database
                        if item.has_column('field_responses'):
                            # extract the custom fields, and save it into form_responses
                            # Processing the Custom Fields (if any)
                            responses = []
                            for custom in item.field_responses:
                                custom.form_id = item.form_id
                                custom.formid = item.formid
                                custom.previous_form_id = item.previous_form_id
                                if item.previous_form_id:
                                    custom.form_id = item.previous_form_id
                                # Set Client and OrgId:
                                custom.client_id = item.client_id
                                custom.orgid = item.orgid
                                responses.append(custom)
                            try:
                                async with self._pgoutput as conn:
                                    await conn.upsert_many(
                                        responses,
                                        table_name='form_responses',
                                        schema='networkninja',
                                        primary_keys=["form_id", "formid", "column_name"],
                                    )
                            except Exception as e:
                                self._logger.warning(
                                    f"Error saving Field Responses: {e}"
                                )
                        # Then, this completed visit will be returned:
                        visit = pd.DataFrame([item])
                        visit['store_id'] = item.store_number.store_id
                        visit['store_name'] = item.store_number.store_name
                        visit['store_number'] = item.store_number.store_number
                        # Drop Unused columns:
                        visit = visit.drop(
                            columns=['user_id', 'store_custom_fields', 'event_id'],
                            errors='ignore'
                        )

                        # Remove duplicate fields from field_responses before exploding
                        def clean_field_responses(responses):
                            if isinstance(responses, list):
                                for response in responses:
                                    if isinstance(response, dict):
                                        # Remove fields that will conflict with main columns
                                        response.pop('orgid', None)
                                        response.pop('client_id', None)
                                        response.pop('form_id', None)
                                        response.pop('formid', None)
                            return responses
                        # Explode the field_responses column
                        # Apply the cleaning function
                        visit['field_responses'] = visit['field_responses'].apply(clean_field_responses)
                        visit = visit.explode('field_responses', ignore_index=True)
                        # Convert each dict in 'field_responses' into separate columns
                        visit = pd.concat(
                            [visit.drop(['field_responses'], axis=1), visit['field_responses'].apply(pd.Series)],
                            axis=1
                        )
                        # Append the visit to the results
                        results.append(visit)
                    # Converting into a Pandas Dataframe
                    continue
                if data_type == 'form':
                    # Sincronize Organization and Client:
                    try:
                        orgid = item.client_id.orgid
                        await orgid.on_sync()
                    except Exception as e:
                        self._logger.error(
                            f"Error saving Organization: {e}"
                        )
                    try:
                        clientid = item.client_id
                        await clientid.on_sync()
                    except Exception as e:
                        self._logger.error(
                            f"Error saving Client: {e}"
                        )
                    # convert to JSON format
                    item.question_blocks = json_encoder(
                        item.question_blocks
                    )
                elif data_type == 'form_metadata':
                    item.column_name = str(item.column_name)
                elif data_type == 'staffing_user':
                    # Saving the Staffing User
                    try:
                        await item.on_sync()
                    except Exception as e:
                        self._logger.error(
                            f"Error saving Staffing User: {e}"
                        )
                    # Then converting lists to JSON:
                    item.custom_fields = json_encoder(
                        item.custom_fields
                    )
                    item.client_names = json_encoder(
                        item.client_names
                    )
                elif data_type == 'store_photo':
                    # Saving the Store Photo
                    item.column_name = str(item.column_name)
                    item.question_name = str(item.question_name)
                    item.url_parts = json_encoder(
                        item.url_parts
                    )
                    try:
                        await item.sync()
                        continue
                    except Exception as e:
                        self._logger.error(
                            f"Error saving Store Photo: {e}"
                        )
                elif data_type in ('retailer', 'store_geography'):
                    try:
                        await item.sync()
                    except Exception as e:
                        self._logger.error(
                            f"Error saving Retailer: {e}"
                        )
                elif data_type == 'store':
                    try:
                        await item.on_sync()
                        await item.save(
                            pk=['store_number'],
                            table_name='stores',
                            schema='networkninja'
                        )
                    except Exception as e:
                        self._logger.error(
                            f"Error saving Store: {e}"
                        )
                else:
                    # We cannot process other data types yet.
                    continue
                await self.upsert_record(
                    item
                )
            return results

    async def get_batch(self):
        """Handle get_batch operation type

        Uses to download a Batch from NetworkNinja SQS Queue.
        """
        url = f"{self.base_url}/{NETWORKNINJA_ENV}/get_batch"
        if self.batch_id:
            url += f"?batch_id={self.batch_id}"
            self.avoid_acceptance = True  # avoid accepting the batch

        args = {
            "method": "get",
            "url": url,
            "use_proxy": False,
            "return_response": True,
        }

        response, result, error = await self.session(**args)
        if response.status_code == 204:
            # There is no data to download and is normal.
            return {}

        if error:
            raise ComponentError(
                f"Error calling Network Ninja API: {error}"
            )

        if not result:
            raise DataNotFound(
                "No data returned from Network Ninja"
            )

        # Saving Batch for security/auditing purposes in DocumentDB:
        try:
            await self._document.write(
                table='batches',
                schema='networkninja',
                data=[result],
                on_conflict='replace'
            )
        except Exception as e:
            self._logger.error(
                f"Error saving Batch into *batches* auditing catalog: {e}"
            )

        # Then, extract batch id and report to NN:
        batch_id = result.get('batch_id')
        self._logger.notice(
            f"Batch Id: {batch_id}"
        )
        self.add_metric('BATCH_ID', batch_id)
        if self.avoid_acceptance is False:
            # Only report the batch if acceptance is enabled.
            await self.report_batch(batch_id)
        return result

    async def report_batch(self, batch_id: str, report_code: int = 200):
        """Handle report_batch operation type

        Uses to report a Batch to NetworkNinja SQS Queue.
        """
        url = f"{self.base_url}/{NETWORKNINJA_ENV}/report_batch_activity"

        payload = {
            "batch_id": batch_id,
            "status_code": report_code
        }
        args = {
            "url": url,
            "use_proxy": False,
            "payload": payload,
            "full_response": True
        }
        result = None
        try:
            response = await self.api_post(**args)
            # TODO: handle error codes (504, 404, etc)
            if response.status_code != 200:
                if response.status_code == 404:
                    self._logger.error(
                        f"HTTP error: {response.status_code} - Batch {batch_id} not found"
                    )
                elif response.status_code == 504:
                    self._logger.error(
                        f"HTTP error: {response.status_code} - Network Ninja API is unavailable"
                    )
            else:
                result = response.json()
        except Exception as e:
            self._logger.error(
                f"Error Reporting Batch with id {batch_id}: {e}"
            )

        if not result:
            raise DataNotFound(
                "No data returned from Network Ninja"
            )

        # Then, saving the acknowledgement in DocumentDB:
        payload = {
            "current_timestamp": datetime.now(tz=timezone.utc),
            **result
        }
        try:
            await self._document.write(
                table='acknowledgements',
                schema='networkninja',
                data=[result],
                on_conflict='replace'
            )
        except Exception as e:
            self._logger.error(
                f"Error saving Acknowledgement: {e}"
            )
        return result

    async def upsert_record(self, obj: Union[dict, BaseModel], **kwargs):
        # TODO: Discover primary Keys from Model instead from Database.
        if isinstance(obj, BaseModel):
            name = obj.modelName
            pk = self._model_caching.get(name, None)
            if not pk:
                pk = []
                fields = obj.columns()
                for _, field in fields.items():
                    if field.primary_key:
                        pk.append(field.name)
                self._model_caching[name] = pk
            table_name = obj.Meta.name
            schema = obj.Meta.schema
        else:
            pk = kwargs.get('pk', [])
            table_name = kwargs.get('table_name', None)
            schema = kwargs.get('schema', None)
        async with self._pgoutput as conn:
            await conn.do_upsert(
                obj,
                table_name=table_name,
                schema=schema,
                primary_keys=pk,
                use_conn=conn.get_connection()
            )
            return True

    async def replace_record(self, obj: Union[dict, BaseModel], **kwargs):
        # TODO: Discover primary Keys from Model instead from Database.
        if isinstance(obj, BaseModel):
            name = obj.modelName
            pk = self._model_caching.get(name, None)
            if not pk:
                pk = []
                fields = obj.columns()
                for _, field in fields.items():
                    if field.primary_key:
                        pk.append(field.name)
                self._model_caching[name] = pk
            table_name = obj.Meta.name
            schema = obj.Meta.schema
        else:
            pk = kwargs.get('pk', [])
            table_name = kwargs.get('table_name', None)
            schema = kwargs.get('schema', None)
        async with self._pgoutput as conn:
            await conn.do_replace(
                obj,
                table_name=table_name,
                schema=schema,
                primary_keys=pk,
                use_conn=conn.get_connection()
            )
            return True
