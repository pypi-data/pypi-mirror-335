# Copyright (C) 2022-2025 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
from typing import Any
from typing import AsyncIterable
from typing import Callable
from typing import Iterable
from typing import TypeVar

import pydantic
from libcanonical.protocols.itransaction import ITransaction

from canonical.ext.repository import BaseModelRepository
from canonical.ext.google.protocols import IDatastoreEntity
from ._storage import BaseDatastoreStorage

M = TypeVar('M', bound=pydantic.BaseModel)


class DatastoreRepository(BaseModelRepository[M]):
    __module__: str = 'canonical.ext.google.datastore'

    def __init__(
        self,
        model: type[M],
        storage: BaseDatastoreStorage | None = None,
        namespace: str | None = None
    ) -> None:
        self.model = model
        self.namespace = namespace
        self.storage = storage or BaseDatastoreStorage()

    def factory(self, entity: dict[str, Any]) -> M:
        return self.model.model_validate(entity)

    def all(self, sort: Iterable[str] | None = None) -> AsyncIterable[M]:
        return self.storage.query(
            model=self.model,
            namespace=self.namespace,
            sort=sort or None,
            page_size=256
        )

    async def key(self, instance: M, parent: Any | None = None) -> Any:
        k = getattr(instance, '__key__')
        if isinstance(k, int) and k < 0:
            k = await self.storage.allocate_identifier(self.model)
            setattr(instance, '__key__', k)
        return self.storage.entity_key(
            kind=self.model,
            identifier=k,
            parent=parent,
            namespace=self.namespace
        )

    async def get(
        self,
        key: Any,
        transaction: ITransaction | None = None,
        factory: Callable[[dict[str, Any]], M] | None = None
    ) -> M | None:
        if transaction is not None:
            raise NotImplementedError
        return await self.storage.get_model_by_key(
            cls=self.model,
            pk=key,
            namespace=self.namespace,
            factory=lambda e, c: (factory or self.factory)(e)
        )

    async def persist(
        self,
        instance: M,
        transaction: ITransaction | None = None,
        exclude: set[str] | None = None
    ) -> M:
        if transaction is not None:
            raise NotImplementedError
        transaction = transaction or self.storage.client # type: ignore
        k = await self.key(instance)
        e = self.storage.entity_factory(k, instance, exclude_fields=exclude)
        await self.storage.run_in_executor(functools.partial(transaction.put, e)) # type: ignore
        return instance

    async def persist_many(
        self,
        objects: Iterable[M],
        transaction: ITransaction | None = None,
        batch_size: int | None = None,
        exclude: set[str] | None = None
    ) -> Iterable[M]:
        if transaction is not None:
            raise NotImplementedError
        transaction = transaction or self.storage.client # type: ignore
        if not objects:
            return []
        entities: list[IDatastoreEntity] = []
        for obj in objects:
            k = await self.key(obj)
            entities.append(self.storage.entity_factory(k, obj, exclude_fields=exclude))
        await self.storage.run_in_executor(functools.partial(transaction.put_multi, entities)) # type: ignore
        return objects