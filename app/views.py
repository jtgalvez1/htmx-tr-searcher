from flask import render_template, request, session, make_response, redirect, redirect, send_from_directory
import os

from app import app
from .controllers import *
from .oauth import *

@app.before_request
def prereq():
    USER_REQUIRED = ['/favorites', '/history', '/pdf', '/api']
    if (session.get('user') is None and request.path.startswith(tuple(USER_REQUIRED))):
        return redirect('/')
    pass

@app.route('/')
@app.route('/home')
@app.route('/favorites')
@app.route('/history')
@app.route('/search')
def index():

    # initialize for render_template
    title = "UPLB ICS PeakOne"
    words = []

    try:
        page = abs(int(request.args.get('p')))
    except:
        page = 0

    template = 'index.html'
    if page > 0:
        template = 'pdfs.html'


    if request.path == '/favorites':
        results, process_time = get_pdfs_from_db(fields=['ID', 'NAME', 'TITLE', 'AUTHORS', 'ABSTRACT', 'INDEX_TERMS', 'YEAR', 'MONTH'],pdf_list=session['user']['saved_trs'], page=page)
        title = 'Favorites | ' + title
    elif request.path == '/history':
        results, process_time = get_pdfs_from_db(fields=['ID', 'NAME', 'TITLE', 'AUTHORS', 'ABSTRACT', 'INDEX_TERMS', 'YEAR', 'MONTH'],pdf_list=session['user']['view_history'], page=page)
        title = 'View History | ' + title
    elif request.path == '/search':
        query = request.args.get('q')

        if not query:
            redirect('/')

        query = query.lower()
        words = query.split()[:5] # max 5 words for querying

        results, process_time = get_pdfs_by_words(words,page=page)
        title = 'Search | ' + title
    else:
        results, process_time = get_pdfs_from_db(fields=['ID', 'NAME', 'TITLE', 'AUTHORS', 'ABSTRACT', 'INDEX_TERMS', 'YEAR', 'MONTH'],page=page)


    if session.get('user'):
        pdfs = []
        for pdf in results:
            if str(pdf['id']) in session['user'].get('saved_trs').strip('][').split(', '):
                pdfs.append({ **pdf, 'favorite': True })
            else:
                pdfs.append({ **pdf, 'favorite': False })
    
        return render_template(
            template, 
            pdfs=pdfs, 
            page=page,
            title=title, 
            path=request.path, 
            query="%20".join(words)
        )
    else:
        res = make_response(
            render_template(
                template,
                pdfs=results,
                page=page,
                title=title,
                path=request.path,
                query="%20".join(words),
                client_id = app.config['GOOGLE_CLIENT_ID'],
                oauth_callback_url = '/callback'
            )
        )
        res.headers.set('Referrer-Policy', 'no-referrer-when-downgrade')
        res.headers.set('Cross-Origin-Opener-Policy', 'same-origin-allow-popups')
        return res

@app.route('/research_paper/<pdf_name>', methods=['GET'])
def research_paper(pdf_name):
    result, process_time = get_pdfs_from_db(fields=['ID', 'NAME', 'TITLE', 'AUTHORS', 'ABSTRACT', 'INDEX_TERMS', 'YEAR', 'MONTH'],filter={ 'column' : 'NAME', 'value' : pdf_name})
    pdf = result[0]

    if (session.get('user')):
        view_history = session['user']['view_history'].strip('][').split(', ')
        if str(pdf['id']) in view_history:
            view_history.remove(str(pdf['id']))
        view_history.append(str(pdf['id']))
        session['user'] = update_view_history(session['userid'], view_history)

    return render_template('pdf.html', pdf=pdf)

@app.route('/pdf/<pdf_name>')
def send_pdf(pdf_name):
    result, process_time = get_pdfs_from_db(fields=['ID', 'NAME', 'TITLE', 'AUTHORS', 'ABSTRACT', 'INDEX_TERMS', 'YEAR', 'MONTH'],filter={ 'column' : 'NAME', 'value' : pdf_name})
    pdf = result[0]

    view_history = session['user']['view_history'].strip('][').split(', ')
    if str(pdf['id']) in view_history:
        view_history.remove(str(pdf['id']))
    view_history.append(str(pdf['id']))
    session['user'] = update_view_history(session['userid'], view_history)

    print(os.path.join(app.root_path,'static',app.config['PDF_DIR']) + pdf_name)
    return send_from_directory(os.path.join(app.root_path,'static',app.config['PDF_DIR']), pdf_name)

@app.route('/bibtex/<pdf_name>')
def bibtex(pdf_name):
    return generate_bibtex(pdf_name)

@app.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html')



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

@app.route('/api/pdf', methods=['POST'])
def upload_paper():
    return

@app.route('/api/pdf/process', methods=['POST'])
def process_pdf():
    return


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
