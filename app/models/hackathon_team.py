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
    role_desc = fields.CharField(max_length=40, null=True)

    class Meta:
        unique_together = (("team", "user_id"),)


class HackathonTeamSubmissionModel(Model):
    id = fields.IntField(pk=True)
    team: fields.ForeignKeyRelation[HackathonTeamModel] = (
        fields.ForeignKeyField(
            model_name="models.HackathonTeamModel",
            related_name="hackathon_team_submissions",
            on_delete=fields.CASCADE,
        )
    )
    hackathon_id = fields.IntField()
    name = fields.CharField(max_length=255)
    s3_key = fields.CharField(max_length=1024)
    content_type = fields.CharField(max_length=255)
    uploaded_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "team_submissions"
        unique_together = (("team_id", "hackathon_id"),)
