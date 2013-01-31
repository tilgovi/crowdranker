# coding: utf8

import access
import util

@auth.requires_login()
def view_venue():
    """This function enables the view of the ranking of items submitted to a
    venue.  It is assumed that the people accessing this can have full
    information about the venue, including the identity of the submitters."""
    c = db.venue(request.args(0)) or redirect(URL('default', 'index'))
    props = db(db.user_properties.email == auth.user.email).select().first()
    if not access.can_view_submissions(c, props):
	session.flash = T('You do not have access to the submissions of this venue.')
	redirect(URL('venues', 'view_venue', args=[c.id]))
    can_view_ratings = access.can_view_ratings(c, props)
    # Prepares the query for the grid.
    q = (db.submission.venue_id == c.id)
    db.submission.quality.readable = can_view_ratings
    db.submission.error.readable = can_view_ratings
    db.submission.content.readable = False
    db.submission.title.writable = False
    db.submission.content.writable = False
    if c.allow_link_submission:
	db.submission.link.readable = True
    is_editable = False
    fields=[db.submission.title, db.submission.email, db.submission.quality,
	    db.submission.error, db.submission.content]
    if access.can_enter_true_quality:
	fields.append(db.submission.true_quality)
	is_editable = True
	db.submission.true_quality.readable = db.submission.true_quality.writable = True
    links = [
	dict(header=T('Download'), body = lambda r:
	     A(T('Download'), _class='btn',
	       _href=URL('submission', 'download_viewer', args=[r.id, r.content])))]
    if access.can_view_feedback(c, props):
	links.append(dict(header=T('Feedback'), body = lambda r:
			  A(T('Read comments'), 
			    _href=URL('feedback', 'view_feedback', args=[r.id]))))
    grid = SQLFORM.grid(q,
	field_id=db.submission.id,
	csv=True,
	args=request.args[:1],
	user_signature=False,
	details=False, create=False,
	editable=is_editable,
	deletable=False,
	fields=fields,
	links=links,
	)
    title = A(c.name, _href=URL('venues', 'view_venue', args=[c.id]))
    return dict(title=title, grid=grid)


@auth.requires_login()
def view_raters():
    """This function shows the contribution of each user to the total ranking of a venue."""
    c = db.venue(request.args(0)) or redirect(URL('default', 'index'))
    props = db(db.user_properties.email == auth.user.email).select().first()
    if not access.can_view_rating_contributions(c, props):
	session.flash = T('You do not have access to the rater contributions for this venue.')
	redirect(URL('venues', 'view_venue', args=[c.id]))
    # Prepares the query for the grid.
    q = (db.user_accuracy.venue_id == c.id)
    grid = SQLFORM.grid(q,
	user_signature=False, details=True,
	create=False, editable=False, deletable=False,
	fields=[db.user_accuracy.user_id, db.user_accuracy.accuracy, db.user_accuracy.n_ratings],
	)
    title = A(c.name, _href=URL('venues', 'view_venue', args=[c.id]))
    return dict(grid=grid, title=title)
