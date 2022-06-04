#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from datetime import *; from dateutil.relativedelta import *
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
logging.basicConfig(filename='fyyur.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# TODO: connect to a local postgresql database

db.create_all();
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
from models import *

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = db.session.query(Venue).all()
  data = []
  set_venues = set()
  state_venues = []
  state = ''
  city = ''
 
  for venue in venues:
    city = venue.city
    state = venue.state
    if not (venue.city in set_venues):
      set_venues.add(venue.city)
  for v in venues:
    for city in set_venues:
      if city == v.city:
        state_venues.append({
          'id':v.id,
          'name': v.name,
          'num_upcoming_shows':0
        })

    data.append({
      "city": city,
      "state": state,
      "venues": state_venues
    })
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  data = []
  venues = db.session.query(Venue).all()

  for venue in venues:
    print("Venues::", venue)
    if str.lower(search_term) in str.lower(str(venue)):
      data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": 0,
      })

  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id).first()
  print("Venue", venue)
  past = []
  upcoming = []
  loop_shows(venue_id, past, upcoming)
  data = {
  "id": venue.id,
  "name": venue.name,
  "genres": venue.genres,
  "address": venue.address,
  "city": venue.city,
  "state": venue.state,
  "phone": venue.phone,
  "website": venue.website_link,
  "facebook_link": venue.facebook_link,
  "facebook_link": venue.facebook_link,
  "seeking_description": venue.seeking_description,
  "image_link": venue.image_link,
  "past_shows": past,
  "upcoming_shows": upcoming,
  "past_shows_count": len(past_shows(venue_id)),
  "upcoming_shows_count": len(upcoming_shows(venue_id)),
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
  # TODO: insert form data as a new Venue record in the db, instead --done
  # TODO: modify data to be the data object returned from db insertion
  
  try:
    venue = Venue(**request.form)
    db.session.add(venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('An error occured, Venue ' + request.form['name'] + ' was not successfully listed!!!!')
  # TODO: on unsuccessful db insert, flash an error instead. --done
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    return None
  except: 
    db.session.rollback()
    flash('An error occured while deleting venue with id:' + venue_id )
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  finally:
    db.session.close()

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = db.session.query(Artist).all()
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  artists = db.session.query(Artist).all()
  data = []

  for artist in artists:
    if str.lower(search_term) in str.lower(str(artist)):
      data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": 0,
    })
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.filter_by(id=artist_id).first()
  past = []
  upcoming = []
  loop_shows(artist_id, past, upcoming)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past_shows(artist_id)),
    "upcoming_shows_count": len(upcoming_shows(artist_id)),
  }
  
  return render_template('pages/show_artist.html', artist=data)

def loop_shows(id, past, upcoming):
    for show in past_shows(id):
      venue = Venue.query.filter_by(id=show["venue_id"]).first()
      past.append({
      "venue_id": show["venue_id"],
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": format_datetime(str(show["start_time"])) 
    })

      for up in upcoming_shows(id):
        venue = Venue.query.filter_by(id=up["venue_id"]).first()
        upcoming.append({
        "venue_id": up["venue_id"],
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": format_datetime(str(up["start_time"])) 
      })
def past_shows(id):
  past = []
  shows = db.session.query(Show).all()
  for show in shows:
    if format_datetime(str(show.start_time)) < format_datetime(str(datetime.now()))  and id == show.artist_id or  id == show.venue_id:
     past.append({
       "start_time": show.start_time,
       "venue_id": show.venue_id
     })

  return past

def upcoming_shows(id):
  upcoming = []
  shows = db.session.query(Show).all()
  for show in shows:
    if format_datetime(str(datetime.now()) ) < format_datetime(str(show.start_time)) and id == show.artist_id or  id == show.venue_id:
     upcoming.append({
       "start_time": show.start_time,
       "venue_id": show.venue_id
     })
  return upcoming
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()
  form.name.data = artist.name,
  form.genres.data =  artist.genres,
  form.city.data =  artist.city,
  form.state.data =  artist.state,
  form.phone.data =  artist.phone,
  form.website_link.data =  artist.website_link,
  form.facebook_link.data =  artist.facebook_link,
  form.seeking_venue.data =  artist.seeking_venue,
  form.seeking_description.data =  artist.seeking_description,
  form.image_link.data =  artist.image_link
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.filter_by(id=artist_id).first()
  try:
    artist.name = request.form["name"],
    artist.genres = request.form["genres"],
    artist.address = request.form["address"],
    artist.city = request.form["city"],
    artist.state =  request.form["state"],
    artist.website_link = request.form["website_link"],
    artist.facebook_link =  request.form["facebook_link"],
    artist.seeking_talent =  request.form["seeking_talent"],
    artist.seeking_description =  request.form["seeking_description"],
    artist.image_link =  request.form["image_link"]
    db.session.commit()

  except:
    db.session.rollback()
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  
  form.name.data = venue.name,
  form.genres.data = venue.genres,
  form.address.data = venue.address,
  form.city.data = venue.city,
  form.state.data = venue.state,
  form.website_link.data = venue.website_link,
  form.facebook_link.data = venue.facebook_link,
  form.seeking_talent.data = venue.seeking_talent,
  form.seeking_description.data = venue.seeking_description,
  form.image_link.data = venue.image_link
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  try:
    venue.name = request.form["name"]
    venue.genres = request.form["genres"]
    venue.address = request.form["address"]
    venue.city = request.form["city"]
    venue.state = request.form["state"]
    venue.website_link = request.form["website_link"]
    venue.facebook_link = request.form["facebook_link"]
    venue.seeking_talent = request.form["seeking_talent"]
    venue.seeking_description = request.form["seeking_description"]
    venue.image_link = request.form["image_link"]
    db.session.commit()
  except: 
    db.session.rollback()
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  try:
    artist = Artist(**request.form)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = db.session.query(Show).all()
  data = []
  for show in shows:
   artist = Artist.query.filter_by(id=show.artist_id).first()
   venue = Venue.query.filter_by(id=show.venue_id).first()
   data.append({
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": format_datetime(str(show.start_time))
     })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  show = Show(**request.form)
  try:
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()

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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
