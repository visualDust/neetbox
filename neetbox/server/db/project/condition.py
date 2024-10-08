# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240116

import json
from typing import Dict, Tuple, Union

from neetbox._protocol import *

from ..abc import SortType


class ProjectDbQueryCondition:
    def __init__(
        self,
        id: Union[Tuple[int, int], int] = None,
        timestamp: Union[Tuple[str, str], str] = None,
        series: str = None,
        run_id: Union[str, int] = None,
        limit: int = None,
        order: Dict[str, SortType] = {},
    ) -> None:
        self.id_range = id if isinstance(id, tuple) else (id, None)
        self.timestamp_range = timestamp if isinstance(timestamp, tuple) else (timestamp, None)
        self.series = series
        self.run_id = run_id
        self.limit = limit
        self.order = {order[0], order[1]} if isinstance(order, tuple) else order

    @classmethod
    def loads(cls, json_data):
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
        return ProjectDbQueryCondition(
            id=id_range,
            timestamp=timestamp_range,
            series=series,
            run_id=run_id,
            limit=limit,
            order=order,
        )

    def dumpt(self):
        query_cond_vars = []
        # === id condition ===
        _id_cond_str = ""
        if self.id_range[0]:
            _id_0, _id_1 = self.id_range
            if _id_1 is None:
                _id_cond_str = f"{ID_COLUMN_NAME} = ?"
                query_cond_vars.append(_id_0)
            else:
                _id_cond_str = f"{ID_COLUMN_NAME} BETWEEN ? AND ?"
                query_cond_vars.append(_id_0)
                query_cond_vars.append(_id_1)
        # === timestamp condition ===
        _timestamp_cond_str = ""
        if self.timestamp_range[0]:
            _ts_0, _ts_1 = self.timestamp_range
            if _ts_1 is None:
                _timestamp_cond_str = f"{TIMESTAMP_COLUMN_NAME} >= ?"
                query_cond_vars.append(_ts_0)
            else:
                _timestamp_cond_str = f"{TIMESTAMP_COLUMN_NAME} BETWEEN ? AND ?"
                query_cond_vars.append(_ts_0)
                query_cond_vars.append(_ts_1)
        # === series condition ===
        _series_cond_str = ""
        if self.series:
            _series_cond_str = f"{SERIES_COLUMN_NAME} = ?"
            query_cond_vars.append(self.series)
        # === run-id condition ===
        _run_id_cond_str = ""
        if self.run_id:
            _run_id_cond_str = f"{RUN_ID_COLUMN_NAME} = ?"
            query_cond_vars.append(self.run_id)
        # === ORDER BY ===
        _order_cond = f"ORDER BY " if self.order else ""
        if self.order:
            for _col_name, _sort in self.order.items():
                _order_cond += (
                    f"{_col_name} {_sort.value if isinstance(_sort,SortType) else _sort}, "
                )
            _order_cond = _order_cond[:-2]  # remove last ','
        # === LIMIT ===
        _limit_cond_str = f"LIMIT {self.limit}" if self.limit else ""
        # === concat conditions ===
        query_condition_strs = []
        for cond in [_id_cond_str, _timestamp_cond_str, _series_cond_str, _run_id_cond_str]:
            if cond:
                query_condition_strs.append(cond)
        query_condition_strs = " AND ".join(query_condition_strs)
        # === concat order by and limit ===
        order_and_limit = []
        for cond in [_order_cond, _limit_cond_str]:
            if cond:
                order_and_limit.append(cond)
        order_and_limit = " ".join(order_and_limit)
        # result
        if query_condition_strs:
            query_condition_strs = f"WHERE {query_condition_strs}"
        query_cond_str = f"{query_condition_strs} {order_and_limit}"
        return query_cond_str, query_cond_vars
