$(function(){
    timer = setInterval("get_new_posts()", 5000);
    var scroll = (document.scrollingElement || document.body);
    scroll.scrollTop = scroll.scrollHeight;
});
offset_value=1;
function get_new_posts(){
    $.getJSON("/post_ajax", {
        book_id: book_id
    }, function(data){
        $('#post-form').before(data['data']);
    });
};
function load_old_posts(){
    $.getJSON("/load_old_posts", {
        book_id: book_id,
        offset_value: offset_value
    }, function(data){
        if(data['data']){
            hidden_id = "load_post_" + offset_value
            hidden_tag = '<div id="' + hidden_id + '"></div>'
            $(hidden_tag).insertAfter('#load_post_button');
            $(data['data']).insertAfter('#load_post_button');
            $('body, html').animate({scrollTop: $("#" + hidden_id).offset().top}, 0);
            offset_value += 1;
        }
    });
};
