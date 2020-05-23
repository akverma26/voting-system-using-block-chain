import smtplib
from email.message import EmailMessage
from django.conf import settings
from django.utils import timezone

import random, string, datetime, time
from django.forms.models import model_to_dict

from .models import Voters, PoliticalParty, Vote, Block, VoteBackup, MiningInfo
from .merkle_tool import MerkleTools

from Crypto.Hash import SHA3_256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

EMAIL_ADDRESS = settings.EMAIL_ADDRESS
EMAIL_PASSWORD = settings.EMAIL_PASSWORD

def send_email_otp(email_to):
    otp = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(8))
    msg = EmailMessage()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email_to
    msg['Subject'] = 'Don\'t reply, OTP for email verfication'
    content = 'Verify your email id to get the private key to cast your priceless vote. '+ otp +' is your OTP for email verfication.\nThank you.'
    msg.set_content(content)
    msg.add_alternative('''\
        <!DOCTYPE html>
        <html>
            <body>
                Verify your email id to get the private key to cast your priceless vote.
                <h2 style="display:inline;">'''+ otp +'''</h2> is your OTP for email verfication.<br>
                Thank you.
            </body>
        </html>
    ''', subtype='html')

    try:
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        return [True, otp]
    except Exception as e:
        return [False, str(e)]

def send_email_private_key(email_to, private_key):
    msg = EmailMessage()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email_to
    msg['Subject'] = 'Don\'t reply, PRIVATE KEY for vote casting.'
    content = 'Paste the Following Private as it is in order to cast your vote.\n\n\n'+ private_key + '\n\n\nNOTE: DON\'T REMOVE -----BEGIN PRIVATE KEY----- AND -----BEGIN PRIVATE KEY-----.\n\nThank you.'
    msg.set_content(content)

    try:
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        return [True]
    except Exception as e:
        return [False, str(e)]

def generate_keys():

    key = ECC.generate(curve='P-256')
    private_key = key.export_key(format='PEM')
    public_key = key.public_key().export_key(format='PEM')

    return private_key, public_key

def verify_vote(private_key, public_key, ballot):

    try:
        signer = DSS.new(ECC.import_key(private_key), 'fips-186-3')
        verifier = DSS.new(ECC.import_key(public_key), 'fips-186-3')
        
        ballot_hash = SHA3_256.new(ballot.encode())

        ballot_signature = signer.sign(ballot_hash)

        verifier.verify(ballot_hash, ballot_signature)
        return [True, 'Your vote verfied and Ballot is signed successfully.', ballot_hash.hexdigest(), ballot_signature.hex()]
    except Exception as e:
        return [False, str(e), 'N/A', 'N/A']

def vote_count():
    parties_id = PoliticalParty.objects.values_list('party_id', flat = True)
    votes = Vote.objects.all()
    vote_result = {party: votes.filter(vote_party_id = party).count() for party in parties_id}
    # print(vote_result)
    return vote_result

