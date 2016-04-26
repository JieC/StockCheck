"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle
from bottle import request,debug,template,redirect,static_file
from google.appengine.api import urlfetch,mail
from google.appengine.ext import ndb
from xml.etree import ElementTree
from datetime import datetime
import logging



# Create the Bottle WSGI application.
bottle = Bottle()
debug(True)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

s = {
    'Microsoft': {
        'qurl': 'http://www.microsoftstore.com/store?Action=DisplayPage&Locale=en_US&SiteID=msusa&id=ProductInventoryStatusXmlPage&productID={pid}',
        'purl': 'http://www.microsoftstore.com/store/msusa/en_US/pdp/productID.{pid}',
        'in': 'PRODUCT_INVENTORY_IN_STOCK',
        'out': 'PRODUCT_INVENTORY_OUT_OF_STOCK',
        'path': './/inventoryStatus'
    },
    'Walmart': {
        'qurl': 'http://api.walmartlabs.com/v1/items/{pid}?apiKey=sbwsb4avhzmze33bges5yunr&format=xml',
        'purl': 'http://www.walmart.com/ip/{pid}',
        'in': 'Available',
        'out': 'Not available',
        'path': './/stock'
    }
}

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
 
@bottle.route('/ref/<name>')
def refresh(name='Microsoft'):
    products = Product.query(Product.store == name).fetch()
    for product in products:
        url = s[name]['qurl'].format(pid=product.key.id())
        result = urlfetch.fetch(url, deadline=15)
        if result.status_code == 200:
            try:
                xml = ElementTree.fromstring(result.content)
                stock = xml.findtext(s[name]['path'])
            except:
                stock = 'Invalid ID'

            if stock == s[name]['in']:
                if product.instock == 'No':
                    send_mail(product.key.id(), product.pname, product.store)
                product.instock = 'Yes'
            elif stock == s[name]['out']:
                product.instock = 'No'
            else:
                product.instock = stock

            product.put()
        

@bottle.route('/add', method='POST')
def do_add():
    pid = request.forms.get('pid').strip()
    pname = request.forms.get('pname')
    pstore = request.forms.get('pstore')
    product = Product(id=pid, pname=pname, instock='Pending', store=pstore)
    product.put()
    redirect('/')

@bottle.route('/del', method='POST')
def do_del():
    pid = request.forms.get('pid')
    product_key =  ndb.Key(Product, pid)
    product_key.delete()
    return 'success'

@bottle.route('/up')
def do_update():
    product_key =  ndb.Key(Product, '123')
    product = product_key.get()
    product.rdate = product.rdate
    product.put()

# Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'

class Product(ndb.Model):
    pname = ndb.StringProperty(indexed=False)
    instock = ndb.StringProperty(indexed=False)
    rdate = ndb.DateTimeProperty(auto_now=True,indexed=False)
    store = ndb.StringProperty(default='Microsoft')
    
class Mail(ndb.Model):
    mail = ndb.StringProperty(indexed=False)

def send_mail(pid, pname, store):
    email_key =  ndb.Key('Mail', '1')
    email = email_key.get()
    message = mail.EmailMessage(sender='noreply@istockcheck.appspotmail.com',
                                subject='Back in Stock Notification')
    message.to = email.mail
    message.html = '''
    <h4>Your Product is back in stock now:</h4>
    <p>{pname}</p>
    <a href="{purl}">Click to Buy</a>
    '''.format(purl=s[store]['purl'].format(pid=pid), pname=pname)
    logging.debug(message.html)
    message.send()

