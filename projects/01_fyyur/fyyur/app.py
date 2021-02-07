#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, abort, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#import psycopg2
#from models import db
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
from flask_sqlalchemy import SQLAlchemy
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
'''
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# Migration
migrate = Migrate(app, db)
'''
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

  
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = db.session.query(Venue).all()
  print(data)

  return render_template('pages/venues.html', areas=data)
  '''
  all_areas = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state, Venue.name).group_by(Venue.city, Venue.state, Venue.name).all()
  data=[]
  
  for area in all_areas:
    venue_locations = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data=[]
    for venue in venue_locations:
      venue_data.append({
        "id":venue.id,
        "name":venue.name,
        #"venues":len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
      })
    data.append({
      "name":area.name,
      "city":area.city,
      "state":area.state,
      #"venues":area.venues
    })
  print('wtf')
  return render_template('pages/venues.html', areas=data)
  #print (venue_locations)
  '''

@app.route('/venues/search', methods=['POST'])
def search_venues():
  #search_term = request.form.get('search_term', '')
  search_term = request.form.get('search_term', '')
  venue_results = db.session.query(Venue).filter((Venue.name.ilike(f'%{search_term}%')) | (Venue.city.ilike(f'%{search_term}%'))).all()
  response = []
  data = []
  for venue in venue_results:
      data.append(
        {
          "id": venue.id,
          "name": venue.name
          #"num_upcoming_shows": len(venue.shows)
          #"count":len(search_venue)
          #see 'response' data structure below
        }
      )
      c=len(data)
      print(c)
  response = {
    "data": data,
    "count": len(data)
  }
      
  return render_template('pages/search_venues.html', results=response, search_term=search_term)
 
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  if not venue: 
    return render_template('errors/404.html')

  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []

  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in upcoming_shows_query:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
    })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    # load data from user input on submit
    form = VenueForm(request.form)
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    # validate phone number -- raises exception if invalid
    #phone_validator(phone)
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    #website = form.website.data
    #image_link = form.image_link.data
    #seeking_talent = True if form.seeking_talent.data == 'Yes' else False
    #seeking_description = form.seeking_description.data

    # create new Venue from form data
    venue = Venue(name=name, city=city, state=state, address=address,phone=phone, genres=genres, facebook_link=facebook_link)
    #website=website, image_link=image_link,seeking_talent=seeking_talent, seeking_description=seeking_description)
    
    # add new venue to session and commit to database
    db.session.add(venue)
    db.session.commit()
    
    # flash success if no errors/exceptions
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

'''
@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  print("start delete")
  error = False
  try:
    #if not venue:
    #  flash('No venue to delete')
    #  return redirect('/venues')
    print ("in try block")
    deleteItem = Venue.query.get(venue_id)
    db.session.delete(deleteItem)
    db.session.commit()
  except():
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('an error occured and Venue ' + {deleteItem} + ' was not deleted')
  if not error:
    flash('Venue ' + {deleteItem }+ ' was successfully deleted')
    
  return render_template('pages/venues.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
'''
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  #artist_results = db.session.query.filter(Artist.name.ilike('%{search_artist}%'.format(search_artist))).all()
  artist_results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  response = []
  data = []
  for artist in artist_results:
    data.append(
      {
        "id": artist.id,
        "name": artist.name,
        #"num_upcoming_shows": len(venue.shows)
        #"count":len(search_venue)
        #see 'response' data structure below
      })
    response = {
      "data" : data,
      "count":len(data)
    }
    
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#venue_results = db.session.query(Venue).filter((Venue.name.ilike(f'%{search_term}%')) | (Venue.city.ilike(f'%{search_term}%'))).all()


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = db.session.query(Artist).get(artist_id)
  if artist is None:
    return redirect(url_for('index'))
  else:
    # genres needs to be a list of genre strings for the template
    #genres = [ genre.name for genre in artist.genres ]
    # Get a list of shows, and count the ones in the past and future
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    now = datetime.now()
    for show in artist.shows:
      if show.start_time > now:
        upcoming_shows_count += 1
        upcoming_shows.append({"venue_id": show.venue_id,"venue_name": show.venue.name, "venue_image_link": show.venue.image_link, "start_time": format_datetime(str(show.start_time))})
      if show.start_time < now:
        past_shows_count += 1
        past_shows.append({"venue_id": show.venue_id,"venue_name": show.venue.name,"venue_image_link": show.venue.image_link, "start_time": format_datetime(str(show.start_time))})
  data = {
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "genres": artist.genres,
    "website": artist.website,
    "image_link": artist.image_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue":artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    #"upcoming_shows": artist.upcoming_shows,
    "upcoming_shows_count": upcoming_shows_count,
    #"past_shows":artist.past_shows
  }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

'''
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }'''
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  #return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist(artist_id):
  form = ArtistForm()
  #artist=Artist.query.get(artist_id)
  artist = db.session.query(Artist).filter_by(Artist.id=artist_id).first()
  if artist is None:
    flash('Artist not found!', 'error')
    return redirect('/artists')
  else:
    artist_data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(';'),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "facebook_link": artist.facebook_link,
    "website": artist.website
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist_data)


  '''
  artist = {
    id=artist.id
    name = artist.name
  }'''
  '''
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  '''
  # TODO: populate form with fields from artist with ID <artist_id>
  #return render_template('forms/edit_artist.html', form=form, artist=artist)
  
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def create_artist_form(artist_id):
  form = ArtistForm()
  return render_template('forms/edit_artist.html', form=form)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  '''form_data = request.form
  artist.name = form_data['name']
  artist.city = form_data['city']
  artist.state = form_data['state']
  artist.phone = form_data['phone']
  artist.genres = ';'.join(form_data.getlist('genres'))
  artist.image_link = form_data['image_link']
  artist.facebook_link = form_data['facebook_link']
  artist.website = form_data['website']
  artist.seeking_venue = True if form_data['seeking_venue']=='true' else False
  artist.seeking_description = form_data['seeking_description']'''
  db.session.commit()

  #return redirect(url_for('show_artist', artist_id=artist_id))
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  #venue = Venue.query.get(venue_id)
  venue = db.session.query(Venue).filter(Venue.id==venue_id).first()
  venue = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(';') if venue.genres else [],
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)



@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False  
  venue = Venue.query.get(venue_id)

  try: 
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash(f'An error occurred. Venue could not be changed.')
  if not error: 
    flash(f'Venue was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    # called upon submitting the new artist listing form
    # load data from user input on submit
    form = ArtistForm(request.form)
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    website = form.website.data
    facebook_link = form.facebook_link.data
    # validate phone number -- raises exception if invalid
    #phone_validator(phone)
    #seeking_venue=seeking_venue,
    #seeking_description=seeking_description,
    #DO NOT USE#new_artist = Artist(
    ##DO NOT USE#name=request.form['name'],

    new_artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, website=website, facebook_link=facebook_link)
    db.session.add(new_artist)
    db.session.commit()
    flash("Artist" + request.form['name'] + 'was successfully added')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

   #venue = Venue(name=name, city=city, state=state, address=address,phone=phone, genres=genres, facebook_link=facebook_link)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows= db.session.query(Show).all()
  #print(shows)
  #need to fix start time
  data = []
  for show in shows:
    artist = show.artist
    venue = show.venue
    data.append({
      "venue_id": venue.id if venue else None,
      "venue_name": venue.name if venue else None,
      "artist_id": artist.id if artist else None,
      "artist_name": artist.name if artist else None,
      "artist_image_link": artist.image_link if artist else None,
      "start_time": str(show.start_time),
    })
  return render_template('pages/shows.html', shows=data)
 

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  show_form = ShowForm(request.form)
  try:
    show = Show(
      artist_id=show_form.artist_id.data,
      venue_id=show_form.venue_id.data,
      start_time=show_form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
    show.add()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. This show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
