from typing import Any, Union
from datetime import datetime, timezone
from datamodel import BaseModel, Field
from asyncdb import AsyncDB
from asyncdb.utils.types import Entity
from navconfig.logging import logging
from querysource.conf import default_dsn, async_default_dsn
from querysource.outputs.tables import PgOutput


class AbstractPayload(BaseModel):
    """Abstract Payload Model.

    Common fields implemented by any Object in NetworkNinja Payloads.
    """
    orgid: int
    inserted_at: datetime = Field(required=False, default=datetime.now)

    async def sync(self, **kwargs):
        """
        Sync the Object with the Database
        """
        return await self.upsert_record(**kwargs)

    async def upsert_record(self, **kwargs):
        """Upsert Record to Database.
        """
        output = PgOutput(dsn=async_default_dsn, use_async=True)
        # Synchronize self object into the database using Upsert.
        fields = self.columns()
        pk = kwargs.get('pk', [])
        if not pk:
            for _, field in fields.items():
                if field.primary_key:
                    pk.append(field.name)
        async with output as conn:
            try:
                if self.Meta.name:
                    await conn.do_upsert(
                        self,
                        table_name=self.Meta.name,
                        schema=self.Meta.schema,
                        primary_keys=pk,
                        use_conn=conn.get_connection()
                    )
                    # await conn.get_connection().commit()
                    return True
                else:
                    logging.warning(
                        f"Unable to Upsert NetworkNinja record: {self.Meta}"
                    )
                    return None
            except Exception as e:
                print('Error Upserting Record >>> ', e)
                logging.error(
                    f"Error Upserting Record: {e}"
                )
                return None

    async def _sync_object(self, conn: Any):
        pass

    async def on_sync(self, upsert: bool = True):
        """
        Sync Current Object with the Database.
        """
        db = AsyncDB('pg', dsn=default_dsn)
        async with await db.connection() as conn:
            await self._sync_object(conn)

    async def save(self, pk: Union[str, list], **kwargs):
        """
        Save the Object to the Database.
        """
        if isinstance(pk, str):
            pk = [pk]
        # Create a string with the WHERE clause (a = 1 AND b = 2)
        conditions = [f"{k} = ${i+1}" for i, k in enumerate(pk)]
        _where = " AND ".join(conditions)
        _values = [getattr(self, k) for k in pk]
        qry = f"SELECT EXISTS (SELECT 1 FROM {self.Meta.schema}.{self.Meta.name} WHERE {_where})"
        db = AsyncDB('pg', dsn=default_dsn)
        async with await db.connection() as conn:
            exists = await conn.fetchval(qry, *_values)
        if exists:
            logging.debug(
                f"Record Exists: {exists} in {self.Meta.schema}.{self.Meta.name}"
            )
            # Making an Upsert:
            return True
            # return await self.upsert_record(pk=pk, **kwargs)
        else:
            # Doing a Faster insert:
            logging.debug(
                f"Inserting new record: {self.Meta.schema}.{self.Meta.name}"
            )
            return await self.insert_record()

    async def insert_record(self, **kwargs):
        """Insert Record to Database.
        """
        # Convert all objects in dataclass into a INSERT statement
        columns = self.get_fields()
        cols = ",".join(columns)
        data = self.to_dict(remove_nulls=True, convert_enums=True, as_values=True)
        _values = ', '.join([f"${i+1}" for i, _ in enumerate(columns)])
        insert = f"INSERT INTO {self.Meta.schema}.{self.Meta.name}({cols}) VALUES({_values})"
        db = AsyncDB('pg', dsn=default_dsn)
        try:
            # Convert data dictionary into a list, ordered by column list:
            source = [data.get(col) for col in columns]
            async with await db.connection() as conn:
                stmt = await conn.engine().prepare(insert)
                result = await stmt.fetchrow(*source, timeout=2)
                logging.debug(f"Result: {result}, Status: {stmt.get_statusmsg()}")
                return True
        except Exception as e:
            logging.error(f"Error Inserting Record: {e}")
            return False
        return False

    async def update_many(
        self,
        objects: list,
        primary_keys: list = None,
        **kwargs
    ):
        """Upsert Several Records in Database.
        """
        output = PgOutput(dsn=async_default_dsn, use_async=True)
        # Synchronize self object into the database using Upsert.
        if not primary_keys:
            fields = self.columns()
            pk = []
            for _, field in fields.items():
                if field.primary_key:
                    pk.append(field.name)
        else:
            pk = primary_keys
        async with output as conn:
            try:
                if self.Meta.name:
                    await conn.update_many(
                        objects,
                        table_name=self.Meta.name,
                        schema=self.Meta.schema,
                        primary_keys=pk,
                        use_conn=conn.get_connection()
                    )
                    return True
                else:
                    logging.warning(
                        f"Unable to Upsert NetworkNinja record: {self.Meta}"
                    )
                    return None
            except Exception as e:
                logging.error(
                    f"Error Upserting Record: {e}"
                )
                return None
