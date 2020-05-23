var selected;

$('#search').on('input',function(){
    for(var party of parties_list_json){
        if( party.party_name.toLowerCase().includes( $('#search').val().toLowerCase() ) ){
            $('#'+party.party_id).css('display','flex');
        }
        else{
            $('#'+party.party_id).css('display','none');
        }
    }
});

// When an option is clicked show div with button to cast vote
$('.option').click(function(){

    if(selected){
        $(selected).find('.party-logo').css('width','90px');
        $(selected).find('img').css('width','90px');
        $(selected).find('.divider').show();
        $(selected).find('.party-name').css({'width':'300px', 'font-size': '20px'});
        $(selected).css({'flex-direction': 'row'});
        $(selected).children('.final-decision').remove();
    }

    selected = this;

    $(this).find('.party-logo').css('width','190px');
    $(this).find('img').css('width','190px');
    $(this).find('.divider').hide();
    $(this).find('.party-name').css({'width':'400px', 'font-size': '30px'});
    $(this).css({'flex-direction': 'column'});

    $(this).append("<div class='final-decision'><a id='vote'>Vote Now</a></div>");
    
    $('#vote').click( function(){
        showAlert('Enter private key sent to your email-id.', 'rgba(201, 136, 255, 0.3)', 'rgb(102, 0, 128)');
        $('.dialog').css('display', 'flex');
        $('.vote-confirmation').removeClass('confirmVoteDialoge-slide-fade-out');
        $('.vote-confirmation').addClass('confirmVoteDialoge-slide-fade-in');
        $('.confirmation-party-logo').attr('src', $(selected).find('img').attr('src'));
        $('.confirmation-party-name').html($(selected).find('.party-name').html());
    });
});

$('#final-confirm').click( function(){
    
    showAlert('Thank you for voting. Please wait...', 'rgba(201, 136, 255, 0.3)', 'rgb(102, 0, 128)');
    var selectedPartyID = $(selected).attr('id');
    var privateKey = $('#private-key-input').val();
    $('.party-selection').remove();
    
    // Flash party logo and name for 2 sec
    $('.all-done').css('display', 'flex');
    $('.voted-party-image').attr('src', $(selected).find('img').attr('src') );    // Set Image of selected Party
    $('.final-message').html('You choose<br>'+$(selected).find('.party-name').html());

    // Hide party logo after 2 sec with some animation
    hideSelectedPartyLogo();

    $.ajax(
        {
            type:'POST',
            url: '/create-vote/',
            data: {'selected-party-id': selectedPartyID, 'private-key':privateKey},
            success: function(data){
                $('.all-done').append(data.html);
                $('.all-done').addClass('all-done-rotate-collapse');

                showFinalStatus();

                if(data.success) {
                    showAlert('Your vote is signed successfully.', 'rgba(136, 255, 156, 0.3)', 'rgb(0, 128, 0)');
                    $('.final-status-row:nth-child(3)').find('td:last-child').css('color', 'rgb(0, 128, 0)');
                }
                else {
                    showAlert('Something went wrong. (Please check status below.)', 'rgba(255, 82, 82, 0.3)', 'rgb(122, 0, 0)', 'vibrate');
                }
            }
        }
    );

});

$('#cancel-confirm').click( function(){

    showAlert('Make your choice. Remember you are going to select a new Representative.', 'rgba(201, 136, 255, 0.3)', 'rgb(102, 0, 128)');

    $('.vote-confirmation').removeClass('confirmVoteDialoge-slide-fade-in');
    $('.vote-confirmation').addClass('confirmVoteDialoge-slide-fade-out');
    setTimeout( function(){
        $('.dialog').css('display', 'none');
    }, 700);
});

function hideSelectedPartyLogo(){
    // Animate Party Image and Name to opacity '0' in 3 sec
    $('.selected-party').animate({
        'opacity': '0'
    }, 2000);

    // Collapse Chosen party image and name and then hide them
    setTimeout( function(){
        $('.selected-party').animate({
            'height': '0',
            'width': '0',
        }, 1000);
        setTimeout(function(){
            $('.selected-party').remove();
        }, 1000);

    }, 2000);
}

function showFinalStatus() {
    setTimeout(function(){
        $('.front').hide();
        $('.final-status').show();
        $('.all-done').removeClass('all-done-rotate-collapse');
        $('.all-done').addClass('all-done-rotate-expand');
    }, 400);

}

// $('#final-confirm').click();