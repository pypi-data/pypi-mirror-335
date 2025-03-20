from ._exceptions import DocumentExistsError, DocumentEmptyError
import threading

class Collection:
    def __init__(self, name: str, database) -> None:
        self.name: str = name
        self._content: list[dict] = []
        self._database = database
        self.full_name = database.name + '.' + self.name

    def _update(self):
        threading.Thread(target=self._database._client.update).start()

    async def find(self) -> list[dict]:
        """
        Returns Raw Data
        """
        return self._content

    async def find_one(self, _filter: dict) -> dict | list[dict]:
        results = []
        for dict in self._content:
            if all([dict.get(k) == v for k, v in _filter.items()]):
                results.append(dict)
        if len(results) == 1:
            return results[0]
        return results
    
    async def insert_one(self, data: dict) -> None:
        if not data:
            raise DocumentEmptyError('The Document you are trying to insert is Empty.')
        if data in self._content:
            raise DocumentExistsError('The Document you are trying to insert already exists.')
        self._content.append(data)
        self._update()

    async def insert_many(self, *data: dict) -> None:
        self._content += data # type: ignore
        self._update()

    async def update_one(self, _filter: dict, data: dict) -> None:
        for idx, dict in enumerate(self._content):
            if all([dict.get(k) == v for k, v in _filter.items()]):
                self._content[idx] = data
        self._update()

    async def delete_one(self, _filter: dict) -> None:
        self._content = [doc for doc in self._content if not all(doc.get(k) == v for k, v in _filter.items())]
        self._update()

    async def delete_many(self, *filters: dict) -> None:
        for _filter in filters:
            await self.delete_one(_filter)
        self._update()

    async def drop(self):
        del self._database.collections[self.name]
        self._update()

    async def truncate(self):
        self.content = []
        self._update()