$(document).ready(function(){
    hide_loading();
    showAlert(
        'Please Enter your Aadhar Card Number to Authenticate yourself in order to cast your pricelsess vote.',
        'rgba(201, 136, 255, 0.3)', 'rgb(102, 0, 128)');
    setTimeout(function(){
        $('.loading-div').css({
            'height': 'calc(100vh - 50px)',
            'top': '50px',
        });
    }, 1000);
})

// Aadhar Validation on input
$('#aadhar').on('input',function(event){
    if($('#aadhar').val().length>12){
        $('#aadhar').val(aadhar);
    }
    if( $.isNumeric( $('#aadhar').val() ) ){
        aadhar = $('#aadhar').val();
    }
    else{
        if($('#aadhar').val().length>0){
            $('#aadhar').val(aadhar);
        }
    }
});

// Authenticate aadhar no after button click
function submit_aadhar() {
    
    show_loading('Please wait, you are being authenticated.');
    $.ajax(
        {
            type:"POST",
            url: "/authentication/",
            data: {'aadhar_no': $('#aadhar').val()},
            success: function( data )
            {
                if(data.success){
                    candidate_details_json = data.details;

                    showAlert(
                        'Successfully Authenticated, Vote Now!',
                        'rgba(136, 255, 156, 0.3)', 'rgb(0, 128, 0)');
                    setTimeout( function(){
                        showAlert(
                            'Please verify an Email-ID, Private key will be sent to this Email-ID.',
                            'rgba(201, 136, 255, 0.3)', 'rgb(102, 0, 128)', null);
                    }, 5000);
                    
                    $('.main-content').html(data.html);
                    hide_loading();
                    showShortDetails();
                }

                else {
                    showAlert(data.error,
                        'rgba(255, 82, 82, 0.3)', 'rgb(122, 0, 0)', 'vibrate');
                    hide_loading();
                }
            }
        }
    );
}

// Show short Details at top right corner after authentication
function showShortDetails() {
    $('.basic-details').html(candidate_details_json.uuid+' ('+candidate_details_json.name+')');
    $('.profile-pic').first().attr('src', candidate_details_json.profile_pic);
    $('.short-details').css('display', 'flex');
}