from flask import url_for
from jinja2.utils import urlize
from flask_login import current_user

from flaskr.utils.template_filters import replace_newline

def make_post_format(posts):
    post_tag = ''
    print('\033[32m'+'✔︎ Test 3 passed'+'\033[0m')
    print(posts)
    for post in posts:
        print('\033[32m'+'✔︎ Test 4 passed'+'\033[0m')
        post_tag += '<div class="col-lg-1 col-md-1 col-sm-2 col-2">'
        post_tag += f'''
            <p>{post.user.username}</p>
            </div>
            <div class="speech-bubble-dest col-lg-4 col-md-8 col-sm-8 col-9">
        '''
        for splitted_post in replace_newline(post.post):
            post_tag += f'<p>{urlize(splitted_post)}</p>'
        post_tag += '''
            </div>
            <div class="col-lg-7 col-md-3 col-sm-1 col-1"></div>
        '''
        print(post_tag)
    return post_tag


def make_old_post_format(posts):
    post_tag = ''
    print('\033[32m'+'✔︎ Test 1 passed'+'\033[0m')
    for post in posts[::-1]:
        print('\033[32m'+'✔︎ Test 2 passed'+'\033[0m')
        if post.from_user_id == int(current_user.get_id()):
            post_tag += f'<div id="self-post-tag-{post.id}" class="col-lg-1 offset-lg-6 col-md-1 offset-md-2 col-sm-1 offset-sm-1 col-1"></div>'
            post_tag += '<div class="speech-bubble-self col-lg-4 col-md-8 col-sm-8 col-9">'
            for splitted_post in replace_newline(post.post):
                post_tag += f'<p>{urlize(splitted_post)}</p>'
            post_tag += '</div>'
            post_tag += '<div class="col-lg-1 col-md-1 col-sm-2 col-2">'
            post_tag += f'<p>{current_user.username}</p>'
            post_tag += '</div>'
        else:
            post_tag += '<div class="col-lg-1 col-md-1 col-sm-2 col-2">'
            post_tag += f'''
                <p>{post.user.username}</p>
                </div>
                <div class="speech-bubble-dest col-lg-4 col-md-8 col-sm-8 col-9">
            '''
            for splitted_post in replace_newline(post.post):
                post_tag += f'<p>{urlize(splitted_post)}</p>'
            post_tag += '''
                </div>
                <div class="col-lg-7 col-md-3 col-sm-1 col-1"></div>
            '''
    return post_tag
