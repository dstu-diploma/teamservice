from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_hackathon_t_name_de9b6a";
        DROP INDEX IF EXISTS "uid_hackathonte_user_id_b62eae";
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_hackathonte_team_id_8e180e" ON "hackathonteammatesmodel" ("team_id", "user_id");
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_hackathon_t_name_8f0e1a" ON "hackathon_teams" ("name", "hackathon_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_hackathonte_team_id_8e180e";
        DROP INDEX IF EXISTS "uid_hackathon_t_name_8f0e1a";
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_hackathon_t_name_de9b6a" ON "hackathon_teams" ("name");
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_hackathonte_user_id_b62eae" ON "hackathonteammatesmodel" ("user_id");"""
