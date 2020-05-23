var emailmsg1 = 'Please enter a valid Email-ID and verfiy it. Key will be sent to this Email-ID.';
var emailmsg2 = 'Please verify your Email-ID. Key will be sent to this Email-ID.';
var valid_email_pattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;

$(document).ready(function(){
    
    $('.email-alert-msg').addClass('email-alert-msg-slide-fade-in');
    set_email_alert_msg();

    function set_email_alert_msg(){
        if( valid_email_pattern.test($('#email-input').val()) ){
            $('.email-alert-msg').html(emailmsg2);
        }
        else{
            $('.email-alert-msg').html(emailmsg1);
        }
    }

    // Email validation on input
    $('#email-input').on('input', function(){
        set_email_alert_msg();
    })

    // Show or hide input div on button click
    $('#change-email').click(function(){

        if( $(this).html() == 'Change' ){
            $('#email-input').prop('disabled', false);
            $('#email-input').removeClass('email-input');
            $('#email-input').css({'color': 'black', 'text-align': 'left'});
            $(this).html('Done');
            
            $('#send-otp').show();
            $('#verified-badge').hide();
            $('#vote-now').addClass('disabled');
            $('.email-alert-msg').show();
        }
        else{
            $('#email-input').prop('disabled', true);
            $('#email-input').addClass('email-input');
            $('#email-input').css('color', 'white');
            $(this).html('Change');
        }
    });

    // Send otp to email addredd on button click and display verification div
    $('#send-otp').click(function(){

        if( valid_email_pattern.test($('#email-input').val()) ){
        
            if($('#change-email').html()=='Done'){
                $('#email-input').prop('disabled', true);
                $('#email-input').addClass('email-input');
                $('#email-input').css('color', 'white');
                $('#change-email').html('Change');
            }

            show_loading('Please wait, OTP is being sent to your email-id.')

            $.ajax(
                {
                    type:'GET',
                    url: '/send-otp/',
                    data: {'email-id': $('#email-input').val()},
                    success: function(data){
 
                        setTimeout(function(){
                            hide_loading_without_reload();
                        }, 1000);

                        if(data.success){
                            
                            $('.otp-div').removeClass('otp-verification-slide-to-bottom');
                            $('.otp-div').addClass('otp-verification-slide-from-bottom');
                            $('#otp-verfication-email').html($('#email-input').val());
                            $('.otp-verification').show();
                            $('.otp-div').show();
                            showAlert('OTP send to ' + $('#email-input').val() + '.', 'rgba(136, 255, 156, 0.3)', 'rgb(0, 128, 0)');
                        }
                        else {
                            showAlert(data.error, 'rgba(255, 82, 82, 0.3)', 'rgb(122, 0, 0)', 'vibrate');
                        }

                    }
                }
            );

        }
        else {
            $('.email-alert-msg').removeClass('email-alert-msg-slide-fade-in');
            $('.email-alert-msg').addClass('boom');
            setTimeout(function(){
                $('.email-alert-msg').removeClass('boom');
            }, 1000);
        }
    });

    // Verify OTP by entered OTP
    $('#verify').click(function(){

        show_loading('Please wait, we are verifying your email-id.')

        $.ajax(
            {
                type:'GET',
                url: '/verify-otp/',
                data: {'otp-input': $('#otp-input').val()},
                success: function(data){

                    setTimeout(function(){
                        hide_loading_without_reload();
                    }, 1500);

                    if(data.success){

                        $('.otp-div').removeClass('otp-verification-slide-from-bottom');
                        $('.otp-div').addClass('otp-verification-slide-to-bottom');
                        setTimeout(function(){
                            $('.otp-verification').hide();
                            $('.otp-div').hide();
                        }, 500);

                        $('#send-otp').hide();
                        $('#verified-badge').css('display', 'inline');
                        $('#email-input').css('text-align', 'right');
                        $('#vote-now').removeClass('disabled');
                        $('.email-alert-msg').hide();
                        
                        showAlert('Email Verfied.', 'rgba(136, 255, 156, 0.3)', 'rgb(0, 128, 0)');
                    }
                    else {
                        showAlert('Wrong OTP.', 'rgba(255, 82, 82, 0.3)', 'rgb(122, 0, 0)', 'vibrate');
                    }

                }
            }
        );
    });

    // Cancel OTP verification and hide verification div
    $('#cancel-otp').click(function(){
        $('.otp-div').removeClass('otp-verification-slide-from-bottom');
        $('.otp-div').addClass('otp-verification-slide-to-bottom');
        setTimeout(function(){
            $('.otp-verification').hide();
            $('.otp-div').hide();
        }, 500);
    });

    $('#vote-now').click(function(event){

        show_loading('Please wait, Private Key is being sent your email-id.');

        $.ajax(
            {
                type:'GET',
                url: '/get-parties/',
                data: 'None',
                success: function(data){

                    parties_list_json = data.parties;
                    $('.main-content').html(data.html);

                    hide_loading();

                    showAlert('Make your choice. Remember you are going to select a new Representative.', 'rgba(201, 136, 255, 0.3)', 'rgb(102, 0, 128)');
                }
            }
        );
    });

});