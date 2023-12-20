from enum import Enum
import json
from typing import Dict, Tuple, Union
from neetbox._protocol import *


class DbQueryFetchType(str, Enum):
    ALL = "all"
    ONE = "one"
    MANY = "many"


class DbQuerySortType(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class QueryCondition:
    def __init__(
        self,
        id: Union[Tuple[int, int], int] = None,
        timestamp: Union[Tuple[str, str], str] = None,
        series: str = None,
        run_id: Union[str, int] = None,
        limit: int = None,
        order: Dict[str, DbQuerySortType] = {},
    ) -> None:
        self.id_range = id if isinstance(id, tuple) else (id, None)
        self.timestamp_range = timestamp if isinstance(timestamp, tuple) else (timestamp, None)
        self.series = series
        self.run_id = run_id
        self.limit = limit
        self.order = {order[0], order[1]} if isinstance(order, tuple) else order

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        """
        {
            "id" : [int,int], # from,to
            "timestamp" : [str,str], # from,to
            "series" : str, # series name
            "limit" : int,
            "order" : [
                {"column name" : "ASC/DESC"},
                ...
            ]
        }
        """
        # try load id range
        id_range = None
        if ID_COLUMN_NAME in json_data:
            id_range_str = json_data[ID_COLUMN_NAME]
            id_range = eval(id_range_str)
            assert (
                isinstance(id_range, list)
                and len(id_range) == 2
                and type(id_range[0]) is int
                and type(id_range[1]) is int
                or type(id_range) is int
            )
            id_range = tuple(id_range)  # to tuple
        # try load timestamp range
        timestamp_range = None
        if TIMESTAMP_COLUMN_NAME in json_data:
            timestamp_range_str = json_data[TIMESTAMP_COLUMN_NAME]
            timestamp_range = eval(timestamp_range_str)
            assert (
                isinstance(timestamp_range, list)
                and len(timestamp_range) == 2
                and type(timestamp_range[0]) is str
                and type(timestamp_range[1]) is str
                or type(timestamp_range) is str
            )
            # datetime.strptime(timestamp_range[0], DATETIME_FORMAT) # try parse to datetime, makesure its valid
            # datetime.strptime(timestamp_range[1], DATETIME_FORMAT)
            timestamp_range = tuple(timestamp_range)
        # try to load series
        series = json_data[SERIES_COLUMN_NAME] if SERIES_COLUMN_NAME in json_data else None
        # run-id cond
        run_id = json_data[RUN_ID_COLUMN_NAME] if RUN_ID_COLUMN_NAME in json_data else None
        # try load limit
        limit = None
        if "limit" in json_data:
            limit = json_data["limit"]
            assert type(limit) is int
        # try load order
        order = None
        if "order" in json_data:
            order = json_data["order"]
            assert isinstance(order, dict)
        return QueryCondition(
            id=id_range,
            timestamp=timestamp_range,
            series=series,
            run_id=run_id,
            limit=limit,
            order=order,
        )

    def dumps(self):
        # === id condition ===
        _id_cond = ""
        if self.id_range[0]:
            _id_0, _id_1 = self.id_range
            _id_cond = (
                f"{ID_COLUMN_NAME}=={_id_0}"
                if _id_1 is None
                else f"{ID_COLUMN_NAME} BETWEEN {_id_0} AND {_id_1}"
            )
        # === timestamp condition ===
        _timestamp_cond = ""
        if self.timestamp_range[0]:
            _ts_0, _ts_1 = self.timestamp_range
            _timestamp_cond = (
                f"{TIMESTAMP_COLUMN_NAME}>='{_ts_0}'"
                if _ts_1 is None
                else f"{TIMESTAMP_COLUMN_NAME} BETWEEN '{_ts_0} AND '{_ts_1}"
            )
        # === series condition ===
        _series_cond = ""
        if self.series:
            _series_cond = f"{SERIES_COLUMN_NAME} == '{self.series}'"
        # === run-id condition ===
        _run_id_cond = ""
        if self.run_id:
            _run_id_cond = f"{RUN_ID_COLUMN_NAME} == {self.run_id}"
        # === ORDER BY ===
        _order_cond = f"ORDER BY " if self.order else ""
        if self.order:
            for _col_name, _sort in self.order.items():
                _order_cond += (
                    f"{_col_name} {_sort.value if isinstance(_sort,DbQuerySortType) else _sort}, "
                )
            _order_cond = _order_cond[:-2]  # remove last ','
        # === LIMIT ===
        _limit_cond = f"LIMIT {self.limit}" if self.limit else ""
        # === concat conditions ===
        query_conditions = []
        for cond in [_id_cond, _timestamp_cond, _series_cond, _run_id_cond]:
            if cond:
                query_conditions.append(cond)
        query_conditions = " AND ".join(query_conditions)
        # === concat order by and limit ===
        order_and_limit = []
        for cond in [_order_cond, _limit_cond]:
            if cond:
                order_and_limit.append(cond)
        order_and_limit = " ".join(order_and_limit)
        # result
        if query_conditions:
            query_conditions = f"WHERE {query_conditions}"
        query_condition_str = f"{query_conditions} {order_and_limit}"
        return query_condition_str
