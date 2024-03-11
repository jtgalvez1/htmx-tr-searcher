from flask import render_template, request, session, make_response, redirect, abort

from app import app
from .controllers import *
from .oauth import *

@app.route('/')
def index():
    try:
        page = abs(int(request.args.get('p')))
    except:
        page = 0

    results, process_time = get_most_recents()
    # get_pdfs_from_db(['NAME','AUTHORS','YEAR','MONTH','ABSTRACT'])

    if session.get('user'):
        pdfs = []
        for pdf in results:
            if str(pdf['id']) in session['user'].get('saved_trs').strip('][').split(', '):
                pdfs.append({ **pdf, 'favorite': True })
            else:
                pdfs.append({ **pdf, 'favorite': False })

        for pdf in pdfs:
            if pdf['id'] in session['user']['saved_trs'].translate({ord(i): None for i in '[]'}).split(','):
                pdf['favorite'] = True
        return render_template('index.html', pdfs=pdfs, page=page, path='/home')
    else:
        res = make_response(
            render_template(
                'index.html',
                pdfs=results,
                page=page,
                client_id = app.config['GOOGLE_CLIENT_ID'],
                oauth_callback_url = app.config['BASE_URL'] + '/callback',
                path='/home'
            )
        )
        res.headers.set('Referrer-Policy', 'no-referrer-when-downgrade')
        res.headers.set('Cross-Origin-Opener-Policy', 'same-origin-allow-popups')
        return res

@app.route('/home')
@app.route('/favorites')
@app.route('/history')
def home():
    try:
        page = abs(int(request.args.get('p')))
    except:
        page = 0

    if request.path == '/favorites':
        results, process_time = get_pdfs_from_list(session['user']['saved_trs'], page=page)
    elif request.path == '/history':
        results, process_time = get_pdfs_from_list(session['user']['view_history'], page=page)
    else:
        results, process_time = get_most_recents(page=page)
        
    pdfs = []
    if (session.get('user')):
        for pdf in results:
            if str(pdf['id']) in session['user'].get('saved_trs').strip('][').split(', '):
                pdfs.append({ **pdf, 'favorite': True })
            else:
                pdfs.append({ **pdf, 'favorite': False })
    else:
        pdfs = results

    return render_template('pdfs.html', pdfs=pdfs, page=page, path=request.path)



#api routes
@app.route('/api/favorite/<pdfid>', methods=['PUT'])
def save_tr(pdfid):
    saved_trs = session['user']['saved_trs'].strip('][').split(', ')
    if pdfid in saved_trs:
        saved_trs.remove(pdfid)
        output = """<svg class="h-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g id="_01_align_center" data-name="01 align center"><path d="M17.5.917a6.4,6.4,0,0,0-5.5,3.3A6.4,6.4,0,0,0,6.5.917,6.8,6.8,0,0,0,0,7.967c0,6.775,10.956,14.6,11.422,14.932l.578.409.578-.409C13.044,22.569,24,14.742,24,7.967A6.8,6.8,0,0,0,17.5.917ZM12,20.846c-3.253-2.43-10-8.4-10-12.879a4.8,4.8,0,0,1,4.5-5.05A4.8,4.8,0,0,1,11,7.967h2a4.8,4.8,0,0,1,4.5-5.05A4.8,4.8,0,0,1,22,7.967C22,12.448,15.253,18.416,12,20.846Z"/></g></svg> Add to Favorites"""
    else:
        saved_trs.append(pdfid)
        output = """<svg class="h-3" fill='red' xmlns="http://www.w3.org/2000/svg" id="Layer_1" data-name="Layer 1" viewBox="0 0 24 24"><path d="M17.5.917a6.4,6.4,0,0,0-5.5,3.3A6.4,6.4,0,0,0,6.5.917,6.8,6.8,0,0,0,0,7.967c0,6.775,10.956,14.6,11.422,14.932l.578.409.578-.409C13.044,22.569,24,14.742,24,7.967A6.8,6.8,0,0,0,17.5.917Z"/></svg> Remove from Favorites"""

    session['user'] = toggle_favorite(session['userid'], saved_trs)

    return output



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
