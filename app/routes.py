from flask import render_template, url_for, flash, redirect, request,session,send_from_directory
from flask_paginate import Pagination, get_page_parameter
import datetime
from app import app, db
from app.models import User, Post

per_page = 50  # 1ページあたりの投稿数

@app.route('/index')

@app.route('/switch_user', methods=['POST'])
def switch_user():
    user_id = request.form.get('user_id')
    if user_id:
        # セッションに現在のユーザーIDを設定
        session['current_user_id'] = int(user_id)
        flash('User switched.')
    else:
        flash('No user selected.')
    return redirect(url_for('index'))



@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        # POSTリクエストの処理
        text = request.form.get('text')
        current_user_id = session.get('current_user_id')  # セッションからユーザーIDを取得

        if not current_user_id:
            # セッションにユーザーIDがない場合、エラーメッセージをフラッシュしてリダイレクト
            flash('Please select a user before posting.')
            return redirect(url_for('index'))

        # 新しい投稿を作成
        new_post = Post(text=text, author_id=current_user_id,created_at=datetime.datetime.now())
        # DB保存処理
        db.session.add(new_post)
        db.session.commit()
        # 保存後にトップページにリダイレクト
        return redirect(url_for('index'))
    
     # セッションからカレントユーザーIDを取得
    current_user_id = session.get('current_user_id')
    current_user = None
    if current_user_id:
        current_user = User.query.get(current_user_id)

    # GETリクエストの処理
    # Postはページングしてから
    page = request.args.get('page', 1, type=int)  # 現在のページ番号（デフォルトは1）
    # Postモデルから投稿をツリーIDの降順で取得し、ページネーションを適用
    pagination = Post.query.order_by(Post.tree_id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items  # 現在のページの投稿を取得
    users = User.query.all()  # すべてのユーザーを取得

    return render_template('index.html', posts=posts, users=users, current_user=current_user, pagination=pagination)

@app.route('/create_post', methods=['POST'])
def create_post():
    # セッションから現在のユーザーIDを取得
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash('You must select a user before posting.')
        return redirect(url_for('index'))

    post_text = request.form['text']
    if not post_text:
        flash('Post content cannot be empty.')
        return redirect(url_for('index'))
    
    # 最大のtree_idを取得し、新しいtree_idを計算
    max_tree_id = db.session.query(db.func.max(Post.tree_id)).scalar() or 0
    new_tree_id = max_tree_id + 1

    # 明示的に現在の時刻を取得
    created_at = datetime.datetime.now()
    
    new_post = Post(text=post_text, 
                    author_id=current_user_id,
                    tree_id=new_tree_id,
                    tree_position=0,
                    created_at= created_at)
    
    db.session.add(new_post)
    db.session.commit()
    flash('Your post has been created.')
    return redirect(url_for('index'))

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.text = request.form['text']
        # その他のフィールドがあればここで更新
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('index'))  # 'index'はポストが編集された後にリダイレクトするエンドポイントです。
    return render_template('edit_post.html', post=post)  # 'edit_post.html'は編集フォームのテンプレートです。

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('The post has been deleted.')  # ユーザーにメッセージを表示
    return redirect(url_for('index'))  # 'index'はポストが削除された後にリダイレクトするエンドポイントです。


@app.route('/add_reply', methods=['POST'])
def add_reply():
    # フォームからデータを取得    
    current_user_id = session.get('current_user_id')  # セッションから現在のユーザーIDを取得
    parent_id = request.form.get('parent_id')  # リプライする親のID（Tree_idではない）
    reply_text = request.form.get('reply_text')  # リプライのテキスト（ここが変更された点です）

    if not reply_text:
        flash('リプライのテキストデータが送れてない')
        return redirect(url_for('index'))
    
    if not parent_id:
        flash('親IDがねえ!')
        return redirect(url_for('index'))

    # 親投稿を取得
    parent_post = Post.query.get(parent_id)
    if not parent_post:
        flash(parent_id)
        return redirect(url_for('index'))

    # 最後尾の tree_position を取得
    # 差し込み先のTree_idはここで取得する
    last_position = db.session.query(db.func.max(Post.tree_position)).filter_by(tree_id=parent_post.tree_id).scalar()
    if last_position is None:
        # もし何らかの理由で最後尾が取得できない場合は、親の position を使用
        last_position = parent_post.tree_position

    # 明示的に現在の時刻を取得
    created_at = datetime.datetime.now()

    # 新しいリプライを作成
    reply = Post(text=reply_text, tree_id=parent_post.tree_id, 
                 tree_position=last_position + 1, 
                 author_id=current_user_id,
                 created_at= created_at)
    
    # データベースに保存
    db.session.add(reply)
    db.session.commit()

    flash('リプライが追加されました。')
    return redirect(url_for('index'))



@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    same_tree_posts = Post.query.filter_by(tree_id=post.tree_id).order_by(Post.tree_position).all()
    return render_template('post_detail.html', post=post, same_tree_posts=same_tree_posts)


#ユーザープロフィールのあたり
@app.route('/user/<string:username>')
def user_profile(username):

    user = User.query.filter_by(username=username).first_or_404()

    # ページング
    # Postはページングしてから
    page = request.args.get('page', 1, type=int)  # 現在のページ番号（デフォルトは1）
    # Postモデルから投稿をツリーIDの降順で取得し、ページネーションを適用
    pagination = Post.query.filter_by(author_id=user.id).order_by(Post.tree_id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    #pagination = Post.query.filter_by(username=username).order_by(Post.tree_id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items  # 現在のページの投稿を取得


    return render_template('user_profile.html', user=user, posts=posts,pagination=pagination)

@app.route('/user')
def user_list():
    users = User.query.all()  # すべてのユーザーを取得
    return render_template('user_list.html', users=users)


@app.route('/set_current_user', methods=['POST'])
def set_current_user():
    user_id = request.form.get('user_id')
    if user_id:
        # セッションにカレントユーザーのIDを設定
        session['current_user_id'] = user_id
        flash('Current user has been set.')
    else:
        flash('No user was selected.')
    return redirect(url_for('index'))

@app.route('/static-site')
def serve_static_site():
    return send_from_directory(url_for('static', filename='js/jquery-3.7.0.min.js'))