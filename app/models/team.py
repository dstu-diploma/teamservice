from tortoise.models import Model
from tortoise import fields


class TeamModel(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=40, unique=True)

    owner_id = fields.IntField(unique=True)

    class Meta:
        table: str = "teams"


class TeamMatesModel(Model):
    team: fields.ForeignKeyRelation[TeamModel] = fields.ForeignKeyField(
        model_name="models.TeamModel",
        related_name="team_mates",
        on_delete=fields.CASCADE,
    )
    user_id = fields.IntField(unique=True)
