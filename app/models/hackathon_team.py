from tortoise.models import Model
from tortoise import fields


class HackathonTeamModel(Model):
    id = fields.IntField(pk=True)
    hackathon_id = fields.IntField()
    name = fields.CharField(max_length=40)

    class Meta:
        table: str = "hackathon_teams"
        unique_together = (("name", "hackathon_id"),)


class HackathonTeamMatesModel(Model):
    team: fields.ForeignKeyRelation[HackathonTeamModel] = (
        fields.ForeignKeyField(
            model_name="models.HackathonTeamModel",
            related_name="hackathon_team_mates",
            on_delete=fields.CASCADE,
        )
    )
    user_id = fields.IntField()
    is_captain = fields.BooleanField()

    class Meta:
        unique_together = (("team", "user_id"),)
