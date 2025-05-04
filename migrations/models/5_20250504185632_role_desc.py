from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "hackathonteammatesmodel" ADD "role_desc" VARCHAR(40);
        ALTER TABLE "teammatesmodel" ADD "role_desc" VARCHAR(40);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "teammatesmodel" DROP COLUMN "role_desc";
        ALTER TABLE "hackathonteammatesmodel" DROP COLUMN "role_desc";"""
