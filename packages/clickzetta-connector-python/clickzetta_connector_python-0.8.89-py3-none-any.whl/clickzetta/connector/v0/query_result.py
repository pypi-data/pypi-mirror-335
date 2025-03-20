import base64
import enum
import io
import string
from logging import getLogger
from typing import TYPE_CHECKING, Iterator, List, Optional, Tuple

import pyarrow as pa

import clickzetta.connector.v0
from clickzetta.connector.v0._dbapi import MESSAGE_FIELD, Field, proto_to_field
import clickzetta.connector.v0._pandas_utils
from clickzetta.connector.v0.utils import as_timezone

if TYPE_CHECKING:
    import pandas


_log = getLogger(__name__)


def safe_to_py_list(column):
    type = str(column.type)
    # pyarrow does not support type of type month_interval and day_time_interval, see this conversion:
    # https://github.com/apache/arrow/issues/29828
    if type == 'month_interval' or type == "day_time_interval":
        raise NotImplementedError(f"Datatype not supported - {type}. You can use `cast` function to "
                                  "convert to other types and try again.")
    return column.to_pylist()


def arrow_table_to_rows(table: pa.Table, schema: List, time_zone: Optional[str] = None) -> List[Tuple]:
    cols = [safe_to_py_list(c) for c in table.columns]
    row_count = table.num_rows
    rows = []
    for i in range(row_count):
        row = []
        for j, col in enumerate(cols):
            value = col[i]
            if value and schema and schema[j]:
                field_type = schema[j].field_type
                if field_type in ['TIMESTAMP_LTZ', 'TIMESTAMP_NTZ']:
                    value = as_timezone(value, time_zone, field_type == 'TIMESTAMP_NTZ')
            row.append(value)
        rows.append(tuple(row))
    return rows


def parse_embedded_data(
    arrow_buffer: str,
    schema: List[Field],
    time_zone: Optional[str] = None,
    pure_arrow_decoding: bool = True,
) -> List[Tuple]:
    try:
        buffer = base64.b64decode(arrow_buffer)
        with pa.ipc.RecordBatchStreamReader(io.BytesIO(buffer)) as reader:
            table = reader.read_all()
            column_dict = {}
            for index, column_name in enumerate(table.column_names):
                if column_name in column_dict:
                    column_dict[f"{column_name}_{index}"] = index
                else:
                    column_dict[column_name] = index
            new_table = table.rename_columns(list(column_dict.keys()))
            if pure_arrow_decoding:
                return arrow_table_to_rows(new_table, schema, time_zone)
            result = []
            pandas_result = new_table.to_pandas()
            for index, row in pandas_result.iterrows():
                result.append(tuple(row.tolist()))
            return result

    except Exception as e:
        _log.error(
            f"[get_arrow_result] Error while converting from arrow to result: {e}"
        )
        raise Exception(
            f"[get_arrow_result] Error while converting from arrow to result: {e}"
        )

class QueryDataType(enum.Enum):
    Memory = 0
    File = 1


class QueryData(object):
    def __init__(
            self,
            data: Optional[list],
            data_type: QueryDataType,
            file_list: list = None,
            schema: Optional[List] = None,
            time_zone: Optional[str] = None,
            *,
            pure_arrow_decoding: bool = False,
            embedded_result: Optional[List[str]] = None,
    ):
        self.data = data
        self.data_type = data_type
        self.file_list = file_list
        self.schema = schema
        self.time_zone: Optional[str] = time_zone
        self._pure_arrow_decoding = pure_arrow_decoding
        self._embedded_result = embedded_result
        self._fetched_pandas = False

    def _memory_iterator(self) -> Iterator[Tuple]:
        if self.data is not None:
            for row in self.data:
                yield row
        if self._embedded_result is not None:
            for row in self._embedded_result:
                parsed = parse_embedded_data(
                    row, self.schema, self.time_zone, self._pure_arrow_decoding
                )
                for row in parsed:
                    yield row

    def _file_iterator(self) -> Iterator[Tuple]:
        for url in self.file_list:
            loaded = self._load_file_result(url)
            for row in loaded:
                yield row

    def __iter__(self) -> Iterator[Tuple]:
        if self.data_type == QueryDataType.Memory:
            return self._memory_iterator()
        elif self.data_type == QueryDataType.File:
            return self._file_iterator()
        else:
            raise RuntimeError(f"Invalid data type {self.data_type}")

    def _load_file_result(self, url: str) -> List[Tuple]:
        from clickzetta.connector.v0.client import _globals

        response = _globals["token_https_session"].get(url, stream=True)
        response.raise_for_status()
        result = []
        stream = io.BytesIO(response.content)
        with pa.ipc.RecordBatchStreamReader(stream) as reader:
            if self._pure_arrow_decoding:
                return arrow_table_to_rows(
                    reader.read_all(), self.schema, self.time_zone
                )
            for index, row in reader.read_pandas().iterrows():
                result.append(tuple(row.to_list()))
            return result

    def fetch_pandas(self) -> Optional["pandas.DataFrame"]:
        if self._fetched_pandas:
            return None
        self._fetched_pandas = True
        return clickzetta.connector.v0._pandas_utils.to_pandas(
            self.schema, self.data, self._embedded_result, self.file_list, self.time_zone)


class QueryResult(object):
    def __init__(self, total_msg, pure_arrow_decoding, timezone_hint=None):
        self.data : QueryData = None
        self.state = None
        self.timezone_hint = timezone_hint
        self.total_row_count = 0
        self.total_msg = total_msg
        self.schema : List[Field] = []
        self._pure_arrow_decoding = pure_arrow_decoding
        self._parse_result_data()
        self._reader : Iterator[Tuple] = None
        self.format = "ARROW"

    def get_result_state(self) -> string:
        return self.total_msg["status"]["state"]

    def get_result_schema(self):
        fields = self.total_msg["resultSet"]["metadata"]["fields"]
        self.schema = [proto_to_field(f) for f in fields]

    def _parse_result_data(self) -> None:
        """
        Parse query results
        - When the query is DDL, the result data is "OPERATION SUCCEED" as the value of data
        - When the query is DML, the result data is the query result
            - If the query result is empty, return an empty list to avoid `query_result.QueryData.read`
              handling an empty list
            - If the query result is not empty, use lazy loading, save the result to embedded_result,
              and finally parse it in `query_result.QueryData.read`
        """
        if len(self.total_msg) == 0:
            return
        self.state = self.total_msg["status"]["state"]
        if self.state != "FAILED" and self.state != "CANCELLED":
            rst = self.total_msg["resultSet"]
            meta = rst["metadata"] if "metadata" in rst else {}
            time_zone = meta["timeZone"] if "timeZone" in meta else self.timezone_hint
            if "data" not in rst:
                if "location" in rst:
                    self.get_result_schema()
                    location = self.total_msg["resultSet"]["location"]
                    presigned_urls = location["presignedUrls"]
                    url_count = len(presigned_urls)
                    _log.info(f"location count: {url_count}")
                    if url_count == 0:
                        self.total_row_count = 0
                        self.data = QueryData(
                            data=[],
                            data_type=QueryDataType.Memory,
                            schema=self.schema,
                            time_zone=time_zone,
                            pure_arrow_decoding=self._pure_arrow_decoding,
                        )
                        return
                    self.data = QueryData(
                        data=None,
                        data_type=QueryDataType.File,
                        file_list=presigned_urls,
                        schema=self.schema,
                        time_zone=time_zone,
                        pure_arrow_decoding=self._pure_arrow_decoding,
                    )
                else:
                    self.schema = [MESSAGE_FIELD]
                    self.total_row_count = 1
                    result_data = [["OPERATION SUCCEED"]]
                    self.data = QueryData(
                        data=result_data,
                        data_type=QueryDataType.Memory,
                        schema=self.schema,
                        time_zone=time_zone,
                        pure_arrow_decoding=self._pure_arrow_decoding,
                    )
            else:
                if not (len(rst["data"]["data"])):
                    self.total_row_count = 0
                    self.get_result_schema()
                    self.data = QueryData(
                        data=[],
                        data_type=QueryDataType.Memory,
                        schema=self.schema,
                        time_zone=time_zone,
                        pure_arrow_decoding=self._pure_arrow_decoding,
                    )
                    return
                self.format = "ARROW" if "format" not in meta else meta["format"].upper()
                result_data = rst["data"]["data"]
                self.get_result_schema()
                if self.format == "TEXT":
                    result = [base64.b64decode(_).decode("utf-8") for _ in result_data]
                    self.data = QueryData(
                        data=result,
                        data_type=QueryDataType.Memory,
                        schema=self.schema,
                        time_zone=time_zone,
                        pure_arrow_decoding=self._pure_arrow_decoding,
                    )
                elif self.format == "ARROW":
                    self.data = QueryData(
                        data=None,
                        data_type=QueryDataType.Memory,
                        schema=self.schema,
                        time_zone=time_zone,
                        pure_arrow_decoding=self._pure_arrow_decoding,
                        embedded_result=result_data
                    )
                else:
                    raise ValueError(f"Unsupported format: {self.format}. Only 'TEXT' and 'ARROW' formats are supported.")

        else:
            raise Exception(
                "SQL job execute failed.Error:" + self.total_msg["status"]["message"]
            )

    @property
    def reader(self) -> Iterator[Tuple]:
        if self._reader is None:
            self._reader = iter(self.data)
        return self._reader
