var aadhar = "";
var candidate_details_json;
var parties_list_json;

// Alert message using innerHTML
function showAlert(inner_html, bg_color, color, animation=null){

    inner_html = '<div class="status"  style="margin-bottom: 10px; color: '+color+'; background: '+bg_color+'">'+inner_html+'</div>';
    $('.status-box').prepend(inner_html);
    $('.status').css('transform', 'translate(0, -33px)')
    $('.status:first-child').addClass('translateStatus');
    $('.status:last-child').addClass('translateStatus2');

    setTimeout(function(){
        $('.status:last-child').remove();
        $('.status').css({'transform': 'translate(0, 0)', 'margin': 'auto'});
    }, 1000);

    if(animation){
        setTimeout(function(){
            $('.status').removeClass('translateStatus');
            $('.status').addClass(animation);
            setTimeout(function(){
                $('.status').removeClass(animation);
            }, 1000);
        }, 1000);
    }
}

// Show Loading
function show_loading(message = 'Please wait...') {
    $('.loading-message').html(message);
    $('.loading-div').css({'display': 'flex', 'opacity': '1'});
}

// Hide Loading
function hide_loading(){

    $('.main-content').hide();
    $('.loading-div').animate(
        {'opacity': '0'},
        {
            duration: 1000,
            complete: function() {
                $('.loading-div').hide();
                $('.main-content').css('display', 'flex');
            }
        }
    );
}

// Hide Loading without reload
function hide_loading_without_reload(){

    $('.loading-div').animate(
        {'opacity': '0'},
        {
            duration: 1000,
            complete: function() {
                $('.loading-div').hide();
            }
        }
    );
}

// Animation during showing drawer
function show_drawer() {
    $('.navigation').show();
    $('.navigation-drawer').removeClass('drawer-slide-to-left');
    $('.navigation-drawer').addClass('drawer-slide-from-left');
    $('.navigation-drawer').show();
}

// Animation during hiding drawer
function hide_drawer() {
    $('.navigation-drawer').removeClass('drawer-slide-from-left');
    $('.navigation-drawer').addClass('drawer-slide-to-left');
    setTimeout(function(){
        $('.navigation-drawer').hide();
        $('.navigation').hide();
    }, 500);
}

$(document).ready(function(){

    // -------------------- Drawer things ----------------------
    $('.logo').click(function(){
        show_drawer();
    });
    
    $('.navigation').click(function(event){
        if($(event.target).prop('class')=='navigation'){
            hide_drawer();
        }
    });
    
    $('.drawer-item-back').click(function(){
        hide_drawer();
    });

    $('#aadhar').val('');
    
    // Disable Right Click
    document.addEventListener('contextmenu', event => event.preventDefault());
});

// 'rgba(201, 136, 255, 0.3)', 'rgb(102, 0, 128)' Normal
// 'rgba(136, 255, 156, 0.3)', 'rgb(0, 128, 0)' Success
// 'rgba(255, 82, 82, 0.3)', 'rgb(122, 0, 0)' Error