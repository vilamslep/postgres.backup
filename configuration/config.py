from configuration.postgres import Postgres
from configuration.folder import Folder
from configuration.email import Email
from configuration.schedule import Schedules
from configuration.utils import Utils

import yaml

class Config:
    postgres: Postgres
    target_folder: Folder
    utils: Utils
    email: Email
    schedules: Schedules

    def load_setting(self, fpath: str):
        with open(fpath) as f:
            setting = yaml.safe_load(f)
            self.postgres         = Postgres(setting['postgres'])
            self.target_folder    = Folder(setting['target_folder'])
            self.utils            = Utils(setting['utils'])
            self.email            = Email(setting['email'])
            self.schedules        = Schedules(setting['schedules'])

    def get_schedules(self) -> Schedules:
        return self.schedules

    def get_connection(self, fn_connect, db:str):
        return self.postgres.create_connection(fn_connect, db)

    def psql(self) -> str:
        return self.utils.psql

    def pg_dump(self) -> str:
        return self.utils.dump

    def compress_tool(self) -> str:
        return self.utils.compress

    def backpath(self) -> str:
        return self.target_folder.path

    def target_folder_auth(self) -> dir:
        return { 'user': self.target_folder.user, 
            'password': self.target_folder.password }

    def database_location(self) -> str:
        return self.postgres.data_location

    def errors(self)-> list[str]:
        return ['pg_dump: ошибка:', 'pg_dump: error:']     
