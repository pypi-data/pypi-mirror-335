from typing import Any, Generator

from google.cloud.datastore import Client, Entity, Key

from gcutils.exceptions import EntityNotFound

# TODO: Maybe create own Entity, where id is always set.


class DSutils:
    __CLIENTS: dict[str, Client] = {}

    def __init__(self, project_id: str) -> None:
        if not project_id in self.__CLIENTS:
            self.__CLIENTS[project_id] = Client(project=project_id)
        self._client: Client = self.__CLIENTS[project_id]

    def get_entity(self, kind: str, id: int | str) -> Entity:
        key = self._client.key(kind, id)  # type: ignore
        return self.get_entity_by_key(key=key)

    def get_entity_by_key(self, key: Key) -> Entity:
        entity: Entity | None = self._client.get(key=key)  # type: ignore
        if not entity:
            raise EntityNotFound(f"Could not find entity with key: {key}")
        return entity

    def get_entities(
        self, keys: list[Key], missing: list[Any] | None = None
    ) -> list[Entity]:
        if missing != []:
            raise ValueError("Missing list must initially be empty")
        entites: list[Entity] = self._client.get_multi(keys=keys, missing=missing)  # type:ignore
        return entites

    def get_entities_by_kind(
        self, kind: str, limit: int | None = None
    ) -> Generator[Entity, None, None]:
        query = self._client.query(kind=kind)
        yield from query.fetch(limit=limit)

    def put(self, entity: Entity) -> None:
        self._client.put(entity=entity)  # type: ignore

    def put_multi(self, entities: list[Entity]) -> None:
        self._client.put_multi(entities=entities)  # type: ignore

    def delete(self, key: Key) -> None:
        self._client.delete(key=key)  # type: ignore

    def delete_multi(self, keys: list[Key]) -> None:
        self._client.delete_multi(keys=keys)  # type: ignore

    def create_complete_keys(self, incomplete_key: Key, num_keys: int) -> list[Key]:
        """
        Incomplete/Partial Key: a Key without an ID/name
        """
        complete_keys: list[Key] = self._client.allocate_ids(
            incomplete_key=incomplete_key, num_ids=num_keys
        )  # type: ignore
        return complete_keys

    def query(self, **kwargs) -> Generator[Entity, None, None]:
        query = self._client.query(**kwargs)
        yield from query.fetch()
