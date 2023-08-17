$(function(){
    // 5秒間隔でget_new_posts関数を実行
    timer = setInterval("get_new_posts()", 5000);
    // 初期画面で画面の一番下にいく
    var scroll = (document.scrollingElement || document.body); //画面をスクロール
    scroll.scrollTop = scroll.scrollHeight;//scrollHeight:スクロールできる分の全体の高さ scrollTop: 垂直方向のスクロールした時の位置(スクロール量)を取得
});
book_id = "{{ book_id }}"; //Jinjaを使って取得
offset_value=1;
function get_new_posts(){
    $.getJSON("/post_ajax", { //Ajaxを使ってメッセージを取得する
        book_id: book_id //jinjaで取得した相手のuser_idをrequest.args.getでuser_idとしてpost_ajaxに渡す
    }, function(data){//post_ajaxより返されたものを全てdata(views.pyの返り値dataとはまた違う)に入れる
        //console.log('test 1')
        $('#post-form').before(data['data']); //formのdivのidを指定しており、formのちょうど上(before)にメッセージが新たに追加される. view.pyよりdata返される
        //console.log('test 2')
    });
};
function load_old_posts(){
    $.getJSON("/load_old_posts", {
        book_id: book_id,
        offset_value: offset_value //関数呼び出し
    }, function(data){
        //console.log('test3')
        if(data['data']){
            //console.log('test4')
            hidden_id = "load_post_" + offset_value
            hidden_tag = '<div id="' + hidden_id + '"></div>'//hiddentagを作成
            $(hidden_tag).insertAfter('#load_post_button'); //hiddentagが入ってその後にデータが読み込まれる。データの下(load_post_buttonの下)にhidden_tagが移動する
            $(data['data']).insertAfter('#load_post_button'); //idがload_post_buttonの後に読み込んだ古いメッセージ(data['data']: make_old_post_format)を追加
            $('body, html').animate({scrollTop: $("#" + hidden_id).offset().top}, 0); //idがhidden_idのhtmlに アニメーションで一瞬で移動することができる. offset.top: htmlの1番上からhtml要素がある座標までの距離
            // scrollTopはスクロールした量のため、idがhidden_idの座標のところまでをスクロール量としてanimateの引数に設定している
            offset_value += 1; //次に読み込むのはさらにもう1個古いメッセージなのでそれを読み込めるように+1する
        }
    });
};
