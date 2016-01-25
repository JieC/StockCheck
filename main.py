"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle
from bottle import request,debug,template
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from xml.etree import ElementTree



# Create the Bottle WSGI application.
bottle = Bottle()
debug(True)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


# Define an handler for the root URL of our application.
@bottle.route('/')
def main():
    q = Product.query().fetch()
    return template('main_template', q=q)
#    for p in q:
#        return p.key.id()

@bottle.route('/ref')
def refresh():
    base_url = 'http://www.microsoftstore.com/store?Action=DisplayPage&Locale=en_US&SiteID=msusa&id=ProductInventoryStatusXmlPage&productID='
    q = Product.query().fetch()
    for p in q:
        url = base_url + p.key.id()
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            xml = ElementTree.fromstring(result.content)
            stock = xml.findtext(".//inventoryStatus")
            p.instock = True if stock == 'PRODUCT_INVENTORY_IN_STOCK' else False
            p.put()
            # PRODUCT_INVENTORY_IN_STOCK PRODUCT_INVENTORY_OUT_OF_STOCK

@bottle.route('/add')
def add():
    return '''
        <form action="/add" method="post">
            Product ID: <input name="pid" type="text" />
            Product Name: <input name="pname" type="text" />
            <input value="Add" type="submit" />
        </form>
    '''

@bottle.route('/add', method='POST')
def do_add():
    pid = request.forms.get('pid').strip()
    pname = request.forms.get('pname')
    product = Product(id=pid, pname=pname)
    product.put()

@bottle.route('/del')
def do_del():
    product_key =  ndb.Key(Product, '123')
    product_key.delete()

@bottle.route('/up')
def do_del():
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
    instock = ndb.BooleanProperty(indexed=False)
    rdate = ndb.DateTimeProperty(auto_now=True)

