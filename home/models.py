from django.db import models

class Voters(models.Model):
    uuid = models.CharField(max_length = 20, primary_key=True)
    name = models.CharField(max_length = 100)
    dob = models.DateField()
    pincode = models.CharField(max_length = 6)
    region = models.CharField(max_length = 100)
    profile_pic = models.CharField(max_length = 500, blank=True)
    email = models.CharField(max_length = 100, blank=True)
    vote_done = models.BooleanField(default = False)

class PoliticalParty(models.Model):
    party_id = models.CharField(max_length=10, primary_key=True)
    party_name = models.CharField(max_length=100)
    party_logo = models.CharField(max_length=500)
    candidate_name = models.CharField(max_length=100, blank=True)
    candidate_profile_pic = models.CharField(max_length=500, blank=True)

class Vote(models.Model):
    uuid = models.CharField(max_length=20, primary_key=True)
    vote_party_id = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    block_id = models.CharField(null=True, max_length=10)

    class Meta:
        ordering = ['-timestamp']

class VoteBackup(models.Model):
    uuid = models.CharField(max_length=20, primary_key=True)
    vote_party_id = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    block_id = models.CharField(null=True, max_length=10)

    class Meta:
        ordering = ['-timestamp']

class Block(models.Model):
    prev_hash = models.CharField(max_length=100, blank=True)
    merkle_hash = models.CharField(max_length=100, blank=True)
    this_hash = models.CharField(max_length=100, blank=True)
    nonce = models.IntegerField(null=True)
    timestamp = models.DateTimeField()

class MiningInfo(models.Model):
    prev_hash = models.CharField(max_length=100, blank=True)
    last_block_id = models.CharField(null=True, max_length=10)
