from flask import Flask, render_template, redirect, url_for
from flaskr.models import BookInfo

app = Flask(__name__)

book_list = [
        BookInfo(0, 'はらぺこあおむし', '絵本', 2000, '2023/2/14', 'image/harapekoaomushi.jpg'),
        BookInfo(1, 'ぐりとぐら', '絵本', 1500, '2023/2/9', 'image/guritogura.jpg'),
        BookInfo(2, '11匹のねこ', '絵本', 1400, '2023/2/20', 'image/11pikinoneko.jpeg'),
        BookInfo(3, 'やさしいC', '専門書', 2750, '2017/5/15', 'image/yasashiiC.jpg')
    ]

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/newtitle')
def load_new_title():
    return render_template('newtitle.html', book_list=book_list)

@app.route('/book/<int:book_number>') #メンバー詳細ページ
def book_detail(book_number):
    for book in book_list:
        if book.number == book_number:
            return render_template('book_detail.html', book=book)
    return redirect(url_for('main')) #いなかったらmainにリダイレクトする

@app.route('/terms') #利用規約
def terms_of_service():
    return render_template('terms.html')

@app.errorhandler(404) #ページが間違うとmain
def redirect_main_page(error):
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)
