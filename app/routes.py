from flask import render_template, request, session, make_response, redirect

from app import app
from . controllers import *
from . oauth import *

@app.route('/')
def index():
    try:
        page = abs(int(request.args.get('p')))
    except:
        page = 0

    pdfs, process_time = get_most_recents()
    # get_pdfs_from_db(['NAME','AUTHORS','YEAR','MONTH','ABSTRACT'])

    if session.get('user'):
        print(session['user']['saved_trs'].translate({ord(i): None for i in '[]'}))
        for pdf in pdfs:
            if pdf['id'] in session['user']['saved_trs'].translate({ord(i): None for i in '[]'}).split(','):
                pdf['favorite'] = True
        return render_template('index.html', pdfs=pdfs, page=page)
    else:
        res = make_response(
            render_template(
                'index.html',
                pdfs=pdfs,
                page=page,
                client_id = app.config['GOOGLE_CLIENT_ID'],
                oauth_callback_url = app.config['BASE_URL'] + '/callback'
            )
        )
        res.headers.set('Referrer-Policy', 'no-referrer-when-downgrade')
        res.headers.set('Cross-Origin-Opener-Policy', 'same-origin-allow-popups')
        return res

@app.route('/home')
def home():
    try:
        page = abs(int(request.args.get('p')))
    except:
        page = 0

    pdfs, process_time = get_most_recents(page=page)

    if (session.get('user')):
        for pdf in pdfs:
            print(pdf)
            if pdf['id'] in session['user']['saved_trs'].translate({ord(i): None for i in '[]'}).split(','):
                pdf['favorite'] = True
            
            print(pdf.get('favorite'))

    return render_template('pdfs.html', pdfs=pdfs, page=page)



#auth routes
@app.route('/callback', methods=['POST', 'GET'])
def callback():
    credential = request.form.get('credential')
    user_google_data = verify_token(credential)
    if user_google_data:
        user = upsert_user(user_google_data)
        session['user'] = { **user, "name" : user.get('given_name') + " " + user.get('family_name') }
        session['userid'] = user_google_data['userid']
        print(session['user'])
        # session['favorites'] = get_user_favoites(user_google_data['userid'])

    return redirect('/')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')
