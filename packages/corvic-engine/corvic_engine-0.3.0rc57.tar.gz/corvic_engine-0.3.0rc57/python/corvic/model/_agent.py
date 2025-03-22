"""Corvic Agents."""

from __future__ import annotations

import copy
import datetime
from collections.abc import Iterable, Sequence
from typing import TypeAlias

from sqlalchemy import orm as sa_orm

from corvic import orm, system
from corvic.model._base_model import BelongsToRoomModel
from corvic.model._defaults import Defaults
from corvic.model._proto_orm_convert import (
    agent_delete_orms,
    agent_orm_to_proto,
    agent_proto_to_orm,
)
from corvic.result import InvalidArgumentError, NotFoundError, Ok
from corvic_generated.model.v1alpha import models_pb2
from corvic_generated.orm.v1.agent_pb2 import AgentParameters

OrgID: TypeAlias = orm.OrgID
RoomID: TypeAlias = orm.RoomID
FeatureViewID: TypeAlias = orm.FeatureViewID
AgentID: TypeAlias = orm.AgentID


class Agent(BelongsToRoomModel[AgentID, models_pb2.Agent, orm.Agent]):
    """A corvic agent represents a named agent that can produce embeddings."""

    @classmethod
    def orm_class(cls):
        return orm.Agent

    @classmethod
    def id_class(cls):
        return AgentID

    @classmethod
    def orm_to_proto(cls, orm_obj: orm.Agent) -> models_pb2.Agent:
        return agent_orm_to_proto(orm_obj)

    @classmethod
    def proto_to_orm(
        cls, proto_obj: models_pb2.Agent, session: orm.Session
    ) -> Ok[orm.Agent] | InvalidArgumentError:
        return agent_proto_to_orm(proto_obj, session)

    @classmethod
    def delete_by_ids(
        cls, ids: Sequence[AgentID], session: orm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return agent_delete_orms(ids, session)

    @classmethod
    def from_id(
        cls,
        agent_id: AgentID,
        client: system.Client | None = None,
        session: sa_orm.Session | None = None,
    ) -> Ok[Agent] | NotFoundError:
        client = client or Defaults.get_default_client()
        return cls.load_proto_for(agent_id, client, existing_session=session).map(
            lambda proto_self: cls(client, proto_self)
        )

    @classmethod
    def from_orm(
        cls,
        agent: orm.Agent,
        client: system.Client | None = None,
    ):
        client = client or Defaults.get_default_client()
        return cls(
            client,
            cls.orm_to_proto(agent),
        )

    @classmethod
    def create(
        cls,
        name: str,
        parameters: AgentParameters,
        room_id: RoomID | None = None,
        client: system.Client | None = None,
    ):
        client = client or Defaults.get_default_client()
        return cls(
            client,
            models_pb2.Agent(
                name=name,
                agent_parameters=parameters,
                room_id=str(room_id or Defaults.get_default_room_id(client)),
            ),
        )

    @classmethod
    def from_proto(
        cls, proto: models_pb2.Agent, client: system.Client | None = None
    ) -> Agent:
        client = client or Defaults.get_default_client()
        return cls(client, proto)

    @classmethod
    def list(
        cls,
        *,
        limit: int | None = None,
        room_id: RoomID | None = None,
        created_before: datetime.datetime | None = None,
        client: system.Client | None = None,
        ids: Iterable[AgentID] | None = None,
        existing_session: sa_orm.Session | None = None,
    ) -> Ok[list[Agent]] | NotFoundError | InvalidArgumentError:
        """List agent models."""
        client = client or Defaults.get_default_client()
        match cls.list_as_proto(
            client,
            limit=limit,
            room_id=room_id,
            created_before=created_before,
            ids=ids,
            existing_session=existing_session,
        ):
            case NotFoundError() | InvalidArgumentError() as err:
                return err
            case Ok(protos):
                return Ok([cls.from_proto(proto, client) for proto in protos])

    @property
    def name(self) -> str:
        return self.proto_self.name

    @property
    def parameters(self) -> AgentParameters:
        return self.proto_self.agent_parameters

    def with_name(self, name: str) -> Agent:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.name = name
        return self.__class__(
            self.client,
            proto_self=proto_self,
        )

    def with_parameters(self, parameters: AgentParameters) -> Agent:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.agent_parameters.CopyFrom(parameters)
        return self.__class__(
            self.client,
            proto_self=proto_self,
        )
