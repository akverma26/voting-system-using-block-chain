from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.forms.models import model_to_dict
from django.contrib import messages
from django.conf import settings
from django.utils import timezone

from .models import Voters, PoliticalParty, Vote, VoteBackup, Block, MiningInfo
from .methods_module import send_email_otp, generate_keys, verify_vote, send_email_private_key, vote_count

from Crypto.Hash import SHA3_256
from .merkle_tool import MerkleTools
import datetime, json, time, random, string

ts_data = {}

# Create your views here.

# -------------- Home (First time loading) --------------
def home(request):
    return render(request, 'home.html')

# --------------- Authentication -------------------
def authentication(request):

    aadhar_no = request.GET.get('aadhar_no')

    details = {'success': False}
    
    try:
        voter = Voters.objects.get(uuid = aadhar_no)
        request.session['uuid'] = aadhar_no
        render_html = loader.render_to_string('candidate_details.html', {'details': voter})
        if voter.vote_done:
            details = {
                'error': 'You have already casted your vote.'
            }
        else:
            details = {
                'success': True,
                'html': render_html,
                'details': model_to_dict(voter)
            }
    except:
        details = {
            'error': 'Invalid Aadhar, Please Enter Correct Aadhar Number!'
        }

    return JsonResponse(details)

# --------- Send otp for email verfication -----------
def send_otp(request):
    email_input = request.GET.get('email-id')

    # [success, result] = send_email_otp(email_input)
    [success, result] = [True, '0']

    json = {'success': success}
    if success:
        request.session['otp'] = result
        request.session['email-id'] = email_input
        request.session['email-verified'] = False
    else:
        json['error'] = result

    return JsonResponse(json)

# -------- Verify email with provided otp ----------
def verify_otp(request):

    otp_input = request.GET.get('otp-input')
    json = {'success': False}
    if otp_input == request.session['otp']:
        voter = Voters.objects.get(uuid = request.session['uuid'])
        voter.email = request.session['email-id']
        voter.save()
        json['success'] = True
        request.session['email-verified'] = True

    return JsonResponse(json)

# --------- On successful email verfication show all parties options ----------
def get_parties(request):
    
    party_list = {}
    if request.session['email-verified']:

        private_key, public_key = generate_keys()

        # send_email_private_key(request.session['email-id'], private_key)
        print(private_key)

        request.session['public-key'] = public_key

        parties = list(PoliticalParty.objects.all())
        parties = [model_to_dict(party) for party in parties]

        render_html = loader.render_to_string('voting.html', {'parties': parties})

        party_list = {
            'html': render_html,
            'parties': parties
        }

    return JsonResponse(party_list)

# ------------- Save vote in database ------------------------
def create_vote(request):

    uuid = request.session['uuid']

    private_key = request.GET.get('private-key')
    public_key = request.session['public-key']

    selected_party_id = request.GET.get('selected-party-id')

    curr = timezone.now()

    ballot = f'{uuid}|{selected_party_id}|{curr.timestamp()}'
    
    status = verify_vote(private_key, public_key, ballot)
    context = {'success': status[0], 'status': status[1]}

    if status[0]:
        try:
            Vote(uuid = uuid, vote_party_id = selected_party_id, timestamp = curr).save()
            VoteBackup(uuid = uuid, vote_party_id = selected_party_id, timestamp = curr).save()
            voter = Voters.objects.get(uuid = request.session['uuid'])
            voter.vote_done = True
            voter.save()
        except Exception as e:
            context['status'] = 'We are not able to save your vote. Please try again. '+str(e)+'.'
            
    html = loader.render_to_string('final-status.html', {
        'ballot': status[2], 'ballot_signature': status[3], 'status': status[1]})
    context['html'] = html

    return JsonResponse(context)

# -------------- create Dummy Data ------------------
def create_dummy_data(request):
    to_do = {
        'createRandomVoters': json.loads(request.GET.get('createRandomVoters')) if request.GET.get('createRandomVoters') else None,
        'createPoliticianParties': json.loads(request.GET.get('createPoliticianParties')) if request.GET.get('createPoliticianParties') else None,
        'castRandomVote': json.loads(request.GET.get('castRandomVote')) if request.GET.get('castRandomVote') else None,
    }
    if to_do['createRandomVoters'] or to_do['createPoliticianParties'] or to_do['castRandomVote']:
        dummy_data_input(to_do)
        return JsonResponse({'success': True})
    return render(request, 'create-dummy-data.html')
    # dummy_data_input()
    # return redirect('/')

# -------------- Show Vote count so far -----------
def show_result(request):
    vote_result = vote_count()
    vote_result = dict(reversed(sorted(vote_result.items(), key = lambda vr:(vr[1], vr[0]))))
    results = []
    political_parties = PoliticalParty.objects.all()
    i=0
    for party_id, votecount in vote_result.items():
        i+=1
        party = political_parties.get(party_id = party_id)
        results.append({
            'sr': i,
            'party_name': party.party_name,
            'party_symbol': party.party_logo,
            'vote_count': votecount
        })
    return render(request, 'show-result.html', {'results': results})

# ------------- Show Block Mining Page -------------
def mine_block(request):
    to_seal_votes_count = Vote.objects.all().filter(block_id=None).count()
    return render(request, 'mine-block.html', {'data': to_seal_votes_count})

# ----------------- Start mining on button click ---------------
def start_mining(request):
    data = create_block()
    html = loader.render_to_string('mined-blocks.html', data)
    return JsonResponse({'html': html})

# Create block [called in start_mining()]
def create_block():

    # Get mining info upto last mining
    mining_info = MiningInfo.objects.all().first()
    prev_hash = mining_info.prev_hash
    curr_block_id = last_block_id = int(mining_info.last_block_id)
    
    non_sealed_votes = Vote.objects.all().filter(block_id=None).order_by('timestamp')
    non_sealed_votes_BACKUP = VoteBackup.objects.all().filter(block_id=None).order_by('timestamp')

    # Get settings for per block mining
    txn_per_block = settings.TRANSACTIONS_PER_BLOCK
    number_of_blocks = int( non_sealed_votes.count()/txn_per_block )

    # Puzzle requirement: '0' * n (n leading zeros)
    puzzle, pcount = settings.PUZZLE, settings.PLENGTH
    
    time_start = time.time()

    result = []

    ts_data['progress'] = True
    ts_data['status'] = 'Mining has been Initialised.'
    ts_data['completed'] = 0

    for _ in range(number_of_blocks):
        # As soon as block_id set to the transaction it is automatically removed from 'non_sealed_vote'
        # Hence always top 'txn_per_block' transactions belong to one block
        block_transactions = non_sealed_votes[:txn_per_block]
        block_transactions_BACKUP = non_sealed_votes_BACKUP[:txn_per_block]
        
        root = MerkleTools()
        root.add_leaf([f'{tx.uuid}|{tx.vote_party_id}|{tx.timestamp}' for tx in block_transactions], True)
        root.make_tree()
        merkle_h = root.get_merkle_root()
        # Try to seal the block and generate valid hash
        nonce = 0
        timestamp = timezone.now()
        while True:
            enc = f'{prev_hash}{merkle_h}{nonce}{timestamp.timestamp()}'.encode('utf-8')
            h = SHA3_256.new(enc).hexdigest()
            if h[:pcount] == puzzle:
                break
            nonce += 1

        # Create the block
        curr_block_id += 1
        Block(id=curr_block_id, prev_hash=prev_hash, merkle_hash=merkle_h, this_hash=h, nonce=nonce, timestamp=timestamp).save()

        result.append({
            'block_id': curr_block_id, 'prev_hash': prev_hash, 'merkle_hash': merkle_h, 'this_hash': h, 'nonce': nonce
        })
        
        # Set this hash as prev hash
        prev_hash = h
        
        # Set block_id to every transaction
        for txn in block_transactions:
            txn.block_id = str(curr_block_id)
            txn.save()
        for txn in block_transactions_BACKUP:
            txn.block_id = str(curr_block_id)
            txn.save()

        ts_data['status'] = str(curr_block_id - last_block_id) + ' blocks have been mined. (' + str((curr_block_id - last_block_id)*txn_per_block) + ' vote transactions have been sealed.)'
        ts_data['completed'] = round((curr_block_id - last_block_id)*100/number_of_blocks)
    time_end = time.time()

    time_taken = time_end - time_start
    if time_taken < 0.0000:
        time_taken = 0.000000

    # Save current Mining info
    mining_info.prev_hash = prev_hash
    mining_info.last_block_id = str(curr_block_id)
    mining_info.id = 0
    mining_info.save()

    data = {
        'time_taken': round(time_end-time_start, 6),
        'result': result
    }

    ts_data['progress'] = False

    return data

def dummy_data_input(to_do):

    ts_data['progress'] = True
    ts_data['status'] = 'Deleting current Data.'
    ts_data['completed'] = 0
    
    PoliticalParty.objects.all().delete()
    Voters.objects.all().delete()
    Vote.objects.all().delete()
    Block.objects.all().delete()
    VoteBackup.objects.all().delete()
    MiningInfo.objects.all().delete()

    ts_data['completed'] = 100
    ts_data['status'] = 'Deleted current Data.'

    MiningInfo(id = 0, prev_hash = '0'*64, last_block_id = '0').save()

    if to_do['createPoliticianParties']:

        parties = {
            'bjp': {
                'party_id': 'bjp',
                'party_name': 'Bhartiya Janta Party (BJP)',
                'party_logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/1/1e/Bharatiya_Janata_Party_logo.svg/180px-Bharatiya_Janata_Party_logo.svg.png',
                'candidate_name': '',
                'candidate_profile_pic': ''
                },
            'congress': {
                'party_id': 'congress',
                'party_name': 'Indian National Congress',
                'party_logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Flag_of_the_Indian_National_Congress.svg/250px-Flag_of_the_Indian_National_Congress.svg.png',
                'candidate_name': '',
                'candidate_profile_pic': ''
                },
            'bsp': {
                'party_id': 'bsp',
                'party_name': 'Bahujan Samaj Party',
                'party_logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Elephant_Bahujan_Samaj_Party.svg/1200px-Elephant_Bahujan_Samaj_Party.svg.png',
                'candidate_name': '',
                'candidate_profile_pic': ''
            },
            'cpi': {
                'party_id': 'cpi',
                'party_name': 'Communist Party of India',
                'party_logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/CPI-banner.svg/200px-CPI-banner.svg.png',
                'candidate_name': '',
                'candidate_profile_pic': ''
            },
            'nota': {
                'party_id': 'nota',
                'party_name': 'None of the above (NOTA)',
                'party_logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/NOTA_Option_Logo.png/220px-NOTA_Option_Logo.png',
                'candidate_name': '',
                'candidate_profile_pic': ''
            }
        }

        ts_data['completed'] = 0
        ts_data['status'] = 'Creating parties.'

        # Create Parties
        for party in parties.values():
            PoliticalParty(party_id = party['party_id'], party_name = party['party_name'], party_logo = party['party_logo']).save()
            curr = list(parties.keys()).index(party['party_id'])+1
            ts_data['completed'] = round(curr*100/len(parties))

    if to_do['createRandomVoters']:

        ts_data['completed'] = 0
        ts_data['status'] = 'Creating voters.'

        # Create Voters
        no_of_voters = 10
        for i in range(1, no_of_voters+1):
            # uuid = ''.join(random.choice(string.digits) for _ in range(12))
            uuid = i
            name = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(12))
            dob = datetime.date(random.randint(1980, 2002), random.randint(1, 12), random.randint(1, 28))
            pincode = ''.join(random.choice(string.digits) for _ in range(6))
            region = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(20))
            voter = Voters(uuid = uuid, name = name, dob = dob, pincode = pincode, region = region).save()
            ts_data['completed'] = round(i*100/no_of_voters)

    if to_do['castRandomVote'] and to_do['createRandomVoters'] and to_do['createPoliticianParties']:

        ts_data['completed'] = 0
        ts_data['status'] = 'Creating votes.'

        # Create Votes
        party_ids = list(parties.keys())
        for i in range(1, no_of_voters+1):
            curr_time = timezone.now()
            party_id = party_ids[random.randint(0,len(party_ids)-1)]
            Vote(uuid = i, vote_party_id = party_id, timestamp = curr_time).save()
            VoteBackup(uuid = i, vote_party_id = party_id, timestamp = curr_time).save()
            voter = Voters.objects.get(uuid=i)
            voter.vote_done = True
            voter.save()
            ts_data['completed'] = round(i*100/no_of_voters)

    ts_data['status'] = 'Finishing task.'
    ts_data['progress'] = False

def blockchain(request):
    blocks = Block.objects.all()
    return render(request, 'blockchain.html', {'blocks':blocks})

def block_info(request):
    try:
        block = Block.objects.get(id=request.GET.get('id'))
        confirmed_by = (Block.objects.all().count() - block.id) + 1

        votes = Vote.objects.filter(block_id=request.GET.get('id'))
        vote_hashes = [SHA3_256.new((f'{vote.uuid}|{vote.vote_party_id}|{vote.timestamp}').encode('utf-8')).hexdigest() for vote in votes]

        root = MerkleTools()
        root.add_leaf([f'{vote.uuid}|{vote.vote_party_id}|{vote.timestamp}' for vote in votes], True)
        root.make_tree()
        merkle_hash = root.get_merkle_root()
        tampered = block.merkle_hash != merkle_hash
        
        context = {
            'this_block': block,
            'confirmed_by': confirmed_by,
            'votes': zip(votes, vote_hashes),
            're_merkle_hash': merkle_hash,
            'isTampered': tampered,
        }
        return render(request, 'block-info.html', context)
    except Exception as e:
        print(str(e))
        return render(request, 'block-info.html')

def sync_block(request):
    try:
        block_id = request.GET.get('block-id')
        print(block_id)
        print(Vote.objects.filter(block_id=block_id))
        backup_votes = VoteBackup.objects.filter(block_id=block_id).order_by('timestamp')
        print(backup_votes)
        for vote in backup_votes:
            x_vote = Vote.objects.get(uuid=vote.uuid)
            x_vote.vote_party_id = vote.vote_party_id
            x_vote.timestamp = vote.timestamp
            x_vote.block_id = vote.block_id
            x_vote.save()
        return JsonResponse({'success': True})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False})

def verify_block(request):
    selected = request.GET.getlist('selected[]')
    context = {}
    for s_block in selected:
        block = Block.objects.get(id=s_block)
        votes = Vote.objects.filter(block_id=s_block)
        vote_hashes = [SHA3_256.new((f'{vote.uuid}|{vote.vote_party_id}|{vote.timestamp}').encode('utf-8')).hexdigest() for vote in votes]

        root = MerkleTools()
        root.add_leaf([f'{vote.uuid}|{vote.vote_party_id}|{vote.timestamp}' for vote in votes], True)
        root.make_tree()
        merkle_hash = root.get_merkle_root()
        tampered = block.merkle_hash != merkle_hash
        context[s_block] = tampered

    return JsonResponse(context)

def track_server(request):
    return JsonResponse(ts_data)
