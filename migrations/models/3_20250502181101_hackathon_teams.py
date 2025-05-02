from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    CREATE TABLE IF NOT EXISTS "hackathon_teams" (
        "id" SERIAL NOT NULL PRIMARY KEY,
        "hackathon_id" INT NOT NULL,
        "name" VARCHAR(40) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS "hackathonteammatesmodel" (
        "id" SERIAL NOT NULL PRIMARY KEY,
        "user_id" INT NOT NULL UNIQUE,
        "is_captain" BOOL NOT NULL,
        "team_id" INT NOT NULL REFERENCES "hackathon_teams" ("id") ON DELETE CASCADE
    );
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "hackathonteammatesmodel";
        DROP TABLE IF EXISTS "hackathon_teams";"""
