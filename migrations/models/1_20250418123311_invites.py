from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "teaminvitesmodel" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user_id" INT NOT NULL,
    "team_id" INT NOT NULL REFERENCES "teams" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_teaminvites_team_id_b90edb" UNIQUE ("team_id", "user_id")
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "teaminvitesmodel";"""
