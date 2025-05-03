from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "hackathon_teams" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "hackathon_id" INT NOT NULL,
            "name" VARCHAR(40) NOT NULL,
            CONSTRAINT "uid_hackathon_t_name_8f0e1a" UNIQUE ("name", "hackathon_id")
        );
        CREATE TABLE IF NOT EXISTS "hackathonteammatesmodel" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "user_id" INT NOT NULL,
            "is_captain" BOOL NOT NULL,
            "team_id" INT NOT NULL REFERENCES "hackathon_teams" ("id") ON DELETE CASCADE,
            CONSTRAINT "uid_hackathonte_team_id_8e180e" UNIQUE ("team_id", "user_id")
        );
        CREATE TABLE IF NOT EXISTS "teams" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(40) NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS "teaminvitesmodel" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "user_id" INT NOT NULL,
            "team_id" INT NOT NULL REFERENCES "teams" ("id") ON DELETE CASCADE,
            CONSTRAINT "uid_teaminvites_team_id_b90edb" UNIQUE ("team_id", "user_id")
        );
        CREATE TABLE IF NOT EXISTS "teammatesmodel" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "user_id" INT NOT NULL UNIQUE,
            "is_captain" BOOL NOT NULL,
            "team_id" INT NOT NULL REFERENCES "teams" ("id") ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS "aerich" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "version" VARCHAR(255) NOT NULL,
            "app" VARCHAR(100) NOT NULL,
            "content" JSONB NOT NULL
        );"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
