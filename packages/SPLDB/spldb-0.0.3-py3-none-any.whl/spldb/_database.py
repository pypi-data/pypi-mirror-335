from ._collection import Collection
import threading

class Database:
    def __init__(self, name: str, client) -> None:
        self.name: str = name
        self.collections: dict[str, Collection] = {}
        self._client = client

    def _update(self):
        threading.Thread(target=self._client.update).start()

    def __getitem__(self, collection_name):
        if collection_name not in self.collections:
            self.collections[collection_name] = Collection(collection_name, self)
        return self.collections[collection_name]    
    
    async def list_collections(self) -> list[str]:
        return list(self.collections)
    
    async def drop(self):
        del self._client.databases[self.name]
        self._update()