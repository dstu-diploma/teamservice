from tortoise.models import Model
from tortoise import fields


class HackathonTeamModel(Model):
    id = fields.IntField(pk=True)
    hackathon_id = fields.IntField()
    name = fields.CharField(max_length=40, unique=True)

    class Meta:
        table: str = "hackathon_teams"


class HackathonTeamMatesModel(Model):
    team: fields.ForeignKeyRelation[HackathonTeamModel] = (
        fields.ForeignKeyField(
            model_name="models.HackathonTeamModel",
            related_name="hackathon_team_mates",
            on_delete=fields.CASCADE,
        )
    )
    user_id = fields.IntField(unique=True)
    is_captain = fields.BooleanField()
