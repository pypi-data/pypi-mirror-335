import dropbox # type: ignore
from ._database import Database
import pickle

class SpLDB:
    def __init__(self, dropbox_access_token) -> None:
        self.DBX_CLIENT = dropbox.Dropbox(dropbox_access_token)
        self.load()

    def __getitem__(self, database_name):
        if database_name not in self.databases:
            self.databases[database_name] = Database(database_name, self)
        return self.databases[database_name]
    
    async def list_databases(self) -> list[str]:
        return list(self.databases)
    
    def load(self) -> None:
        matches = self.DBX_CLIENT.files_search('', 'database.txt')
        if not matches.matches:
            content: dict = {}
        else:
            _, res = self.DBX_CLIENT.files_download('/database.txt')
            content = pickle.loads(res.content)

        self.databases: dict[str, Database] = content
    
    def update(self):
        self.DBX_CLIENT.files_upload(pickle.dumps(self.databases), '/database.txt', mode=dropbox.files.WriteMode("overwrite"))
        print('Updated')