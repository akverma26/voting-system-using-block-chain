var selected = [];
var exp_len, all_check = false;

$(document).ready(function(){
    exp_len = $('.verify-button').find('input').length - 1;
    $('.verify-button').find('input').each(function(){
        $(this).prop('checked', false);
    });

});

function verifySelect(item) {
    
    if(item.checked) {
        if( $(item).parent().parent().parent().attr('id') ) {
            selected.push(parseInt($(item).parent().parent().parent().attr('id')));
            if(selected.length == exp_len) {
                $('.table-header').find('input').prop('checked', true);
            }
        }
        else {

            $('.verify-button').find('input').each(function(){
                $(this).prop('checked', true);

                if( $(this).parent().parent().parent().attr('id') ){
                    var index = selected.indexOf( parseInt($(this).parent().parent().parent().attr('id')) );
                    if(index==-1){
                        selected.push(parseInt($(this).parent().parent().parent().attr('id')));
                    }
                }
            });
        }
    }
    else {
        if( $(item).parent().parent().parent().attr('id') ){
            var index = selected.indexOf( parseInt($(item).parent().parent().parent().attr('id')) );
            if(index>-1) {
                selected.splice(index, 1);
            }
            $('.table-header').find('input').prop('checked', false);
        }
        else {
            $('.verify-button').find('input').each(function(){
                $(this).prop('checked', false);

                if( $(this).parent().parent().parent().attr('id') ){
                    var index = selected.indexOf( parseInt($(this).parent().parent().parent().attr('id')) );
                    if(index>-1){
                        selected.splice(index, 1);
                    }
                }
            });
        }
    }

    selected.sort(function(a, b){return a - b});
}

function verifyBlock(item) {

    if($(item).parent().parent().parent().attr('id')) {
        sendBlockVerifyRequest([$(item).parent().parent().parent().attr('id')])
        $(item).parent().parent().html('Verifying...');
    }
    else {
        sendBlockVerifyRequest(selected);
        for( var ele of selected ) {
            $('#'+ele).find('.verify-button').parent().html('Verifying...');
        }
        if(selected.length == exp_len) {
            $('.table-header').find('.verify-button').parent().html('Verifying...');
            all_check = true;
        }
    }

    $('.verify-button').find('input').each(function(){
        $(this).prop('checked', false);
    });
    selected = [];
    exp_len = $('.verify-button').find('input').length - 1;;
}

function sendBlockVerifyRequest(selected_blocks) {
    
    $.ajax(
        {
            type:'GET',
            url: '/verify-block/',
            data: {'selected[]': selected_blocks},
            success: function(data){
                for( var d in data){
                    if(data[d]){
                        var html = `
                            <span style="color: white; font-size: 16px; font-variant: small-caps; letter-spacing: 2px;">
                                Tampered
                                <br>
                                <a style="font-size: 14px; letter-spacing: 1px; font-varient: normal; text-decoration: underline; cursor: pointer;" onclick = synNow(`+d+`) >
                                    Sync Now
                                </a>
                            </span>'
                        `
                        $('#'+d+' td:last-child').html(html);
                        $('#'+d).css({'background': 'rgb(255, 130, 130)'});
                    }
                    else {
                        $('#'+d+' td:last-child').html('<span style="color:rgb(0,150,0); font-size: 16px; font-variant: small-caps; letter-spacing: 2px;">Verified</span>');
                    }
                    if(all_check) {
                        $('.table-header'+' td:last-child').html('<span style="font-size: 16px; font-variant: small-caps; letter-spacing: 2px;">Result</span>');
                    }
                }
            }
        }
    );
}

function synNow(blocks) {

    // for( var block of blocks ){
        var id = blocks;
        $.ajax(
            {
                type:'GET',
                url: '/sync-block/',
                data: {'block-id': id},
                success: function(data){
                    if(data.success) {
                        $('#'+id).css({'background': 'transparent'});
                        $('#'+id+' td:last-child').html('<span style="color:rgb(0,150,0); font-size: 16px; font-variant: small-caps; letter-spacing: 2px;">Verified</span>');
                    }
                }
    
            }
        );

    // }
}