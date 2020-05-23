from django.contrib import admin

from .models import Voters, Vote, Block, VoteBackup, PoliticalParty, MiningInfo

# Register your models here.
admin.site.register(Voters)
admin.site.register(Vote)
admin.site.register(Block)
admin.site.register(VoteBackup)
admin.site.register(PoliticalParty)
admin.site.register(MiningInfo)
