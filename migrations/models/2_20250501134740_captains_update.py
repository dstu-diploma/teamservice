from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_teams_owner_i_c7afa3";
        ALTER TABLE "teammatesmodel" ADD "is_captain" BOOL NOT NULL;
        ALTER TABLE "teams" DROP COLUMN "owner_id";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "teams" ADD "owner_id" INT NOT NULL UNIQUE;
        ALTER TABLE "teammatesmodel" DROP COLUMN "is_captain";
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_teams_owner_i_c7afa3" ON "teams" ("owner_id");"""
