"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle
from bottle import request, debug, template, redirect, static_file
from google.appengine.api import urlfetch, mail
from google.appengine.ext import ndb
import re
import logging

# Create the Bottle WSGI application.
bottle = Bottle()
debug(True)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

patt = '''schema.org/InStock|setProperty\("inStock", "1"\)|\
product_instock:\['1'\]'''
prog = re.compile(patt)


# Define an handler for the root URL of our application.
@bottle.route('/')
def main():
    q = Product.query().fetch()
    return template('main_template', q=q)


@bottle.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')


@bottle.route('/refall')
def refall():
    products = Product.query().fetch()
    for product in products:
        product.put()


@bottle.route('/ref')
def refresh():
    products = Product.query().fetch()
    for product in products:
        try:
            result = urlfetch.fetch(product.purl, deadline=30)
        except:
            continue
        if result.status_code == 200:
            stock = prog.search(result.content)
            if stock:
                if product.instock in ('No', 'Invalid'):
                    send_mail(product.pname, product.purl)
                product.instock = 'Yes'
            else:
                product.instock = 'No'
        else:
            product.instock = 'Invalid'

        product.put()


@bottle.route('/add', method='POST')
def do_add():
    pname = request.forms.get('pname')
    purl = request.forms.get('purl')
    product = Product(pname=pname, purl=purl, instock='Pending')
    product.put()
    redirect('/')


@bottle.route('/del', method='POST')
def do_del():
    pid = int(request.forms.get('pid'))
    product_key = ndb.Key(Product, pid)
    product_key.delete()
    return 'success'


# Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'


class Product(ndb.Model):
    pname = ndb.StringProperty(indexed=False)
    purl = ndb.StringProperty(indexed=False)
    instock = ndb.StringProperty(indexed=False)
    rdate = ndb.DateTimeProperty(auto_now=True, indexed=False)


class Mail(ndb.Model):
    mail = ndb.StringProperty(indexed=False)


def send_mail(pname, purl):
    email_key = ndb.Key('Mail', '1')
    email = email_key.get()
    message = mail.EmailMessage(sender='noreply@istockc.appspotmail.com',
                                subject='Back in Stock Notification')
    message.to = email.mail
    message.html = '''
    <h4>Your Product is back in stock now:</h4>
    <p>{pname}</p>
    <a href="{purl}">Click to Buy</a>
    '''.format(purl=purl, pname=pname)
    logging.debug(message.html)
    message.send()
