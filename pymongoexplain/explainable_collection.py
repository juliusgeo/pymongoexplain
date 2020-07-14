# Copyright 2020-present MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Union, List

import pymongo
from bson.son import SON

from .commands import AggregateCommand, FindCommand, CountCommand, \
    UpdateCommand, DistinctCommand, DeleteCommand


Document = Union[dict, SON]

class ExplainCollection():
    def __init__(self, collection):
        self.collection = collection
        self.last_cmd_payload = None

    def _explain_command(self, command: Document):
        explain_command = SON([("explain", command.get_SON())])
        explain_command["verbosity"] = "queryPlanner"
        self.last_cmd_payload = explain_command
        return self.collection.database.command(explain_command)

    def update_one(self, filter, update, upsert=False,
                   bypass_document_validation=False,
                   collation=None, array_filters=None, hint=None,
                   session=None, **kwargs):
        kwargs.update(locals())
        del kwargs["self"], kwargs["kwargs"], kwargs["filter"], kwargs["update"]
        command = UpdateCommand(self.collection, filter, update, kwargs)
        return self._explain_command(command)

    def update_many(self, filter: Document, update: Document, upsert=False,
                    array_filters=None, bypass_document_validation=False, collation=None, session=None, **kwargs):
        kwargs.update(locals())
        del kwargs["self"], kwargs["kwargs"], kwargs["filter"], kwargs["update"]
        kwargs["multi"] = True
        command = UpdateCommand(self.collection, filter, update, kwargs)
        return self._explain_command(command)

    def distinct(self, key: str, filter: Document=None, session=None, **kwargs):
        command = DistinctCommand(self.collection, key, filter, session, kwargs)
        return self._explain_command(command)

    def aggregate(self, pipeline: List[Document], session=None, **kwargs):
        command = AggregateCommand(self.collection, pipeline, session,
                                   {},kwargs)
        return self._explain_command(command)

    def count_documents(self, filter: Document, session=None, **kwargs):
        command = CountCommand(self.collection, filter,kwargs)
        return self._explain_command(command)

    def delete_one(self, filter: Document, collation=None, session=None,
                   **kwargs):
        limit = 1
        command = DeleteCommand(self.collection, filter, limit, collation,
                                kwargs)
        return self._explain_command(command)

    def delete_many(self, filter: Document, collation=None,
                    session=None, **kwargs):
        limit = 0
        command = DeleteCommand(self.collection, filter, limit, collation,
        kwargs)
        return self._explain_command(command)

    def watch(self, pipeline: Document = None, full_document: Document = None,
              resume_after= None,
              max_await_time_ms: int = None, batch_size: int = None,
              collation=None, start_at_operation_time=None, session:
            pymongo.mongo_client.client_session.ClientSession=None,
              start_after=None):
        change_stream_options = {"start_after":start_after,
                                 "resume_after":resume_after,
                                "start_at_operation_time":start_at_operation_time,
                                 "full_document":full_document}
        if pipeline is not None:
            pipeline = [{"$changeStream": change_stream_options}]+pipeline
        else:
            pipeline = [{"$changeStream": change_stream_options}]

        command = AggregateCommand(self.collection, pipeline,
                                   session, {"batch_size":batch_size},
                                   {"collation":collation, "max_await_time_ms":
                                       max_await_time_ms})
        return self._explain_command(command)

    def find(self, filter: Document = None, projection: list = None,
             skip: int = 0, limit: int = 0, no_cursor_timeout: bool = False,
             sort: Document = None, allow_partial_results: bool = False,
             oplog_replay: bool = False, batch_size: int=0,
             collation: Document = None, hint: Union[Document, str] = None,
             max_time_ms: int = None, max: Document = None, min: Document =
             None, return_key: bool = False,
             show_record_id: bool = False, comment: str = None,
             session:Document = None, **kwargs: Union[int, str, Document,
                                                      bool]):
        kwargs.update(locals())
        del kwargs["self"], kwargs["kwargs"]
        command = FindCommand(self.collection,
                                kwargs)
        return self._explain_command(command)


