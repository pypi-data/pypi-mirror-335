from ._exceptions import DocumentExistsError, DocumentEmptyError
import threading

class Collection:
    def __init__(self, name: str, database) -> None:
        self.name: str = name
        self.content: list[dict] = []
        self.database = database

    async def find(self) -> list[dict]:
        """
        Returns Raw Data
        """
        return self.content

    async def find_one(self, _filter: dict) -> dict | list[dict]:
        results = []
        for dict in self.content:
            if all([dict.get(k) == v for k, v in _filter.items()]):
                results.append(dict)
        if len(results) == 1:
            return results[0]
        return results
    
    async def insert_one(self, data: dict) -> None:
        if not data:
            raise DocumentEmptyError('The Document you are trying to insert is Empty.')
        if data in self.content:
            raise DocumentExistsError('The Document you are trying to insert already exists.')
        self.content.append(data)
        threading.Thread(target=self.database.client.update).start()

    async def insert_many(self, *data: dict, ignore_exists=True) -> None:
        for each in data:
            if each in self.content:
                if not ignore_exists:
                    raise DocumentExistsError('The Document you are trying to insert already exists.')
            else:
                self.content.append(each)
        threading.Thread(target=self.database.client.update).start()

    async def update_one(self, _filter: dict, data: dict) -> None:
        for idx, dict in enumerate(self.content):
            if all([dict.get(k) == v for k, v in _filter.items()]):
                self.content[idx] = data
        threading.Thread(target=self.database.client.update).start()

    async def delete_one(self, _filter: dict) -> None:
        for idx, dict in enumerate(self.content):
            if all([dict.get(k) == v for k, v in _filter.items()]):
                self.content[idx] = {}
        self.content.remove({})
        threading.Thread(target=self.database.client.update).start()

    async def delete_many(self, *filters: dict) -> None:
        for _filter in filters:
            await self.delete_one(_filter)
        threading.Thread(target=self.database.client.update).start()