"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle
from bottle import request,debug,template,redirect,static_file
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from xml.etree import ElementTree
from datetime import datetime



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

@bottle.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')

@bottle.route('/ref')
def refresh():
    base_url = 'http://www.microsoftstore.com/store?Action=DisplayPage&Locale=en_US&SiteID=msusa&id=ProductInventoryStatusXmlPage&productID='
    products = Product.query().fetch()
    for product in products:
        url = base_url + product.key.id()
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            try:
                xml = ElementTree.fromstring(result.content)
                stock = xml.findtext(".//inventoryStatus")
            except:
                stock = 'Invalid ID'

            if stock == 'PRODUCT_INVENTORY_IN_STOCK':
                if product.instock == 'No':
                    send_mail(product.key.id(), product.pname)
                product.instock = 'Yes'
            elif stock == 'PRODUCT_INVENTORY_OUT_OF_STOCK':
                product.instock = 'No'
            else:
                product.instock = stock

            product.put()
        

@bottle.route('/add', method='POST')
def do_add():
    pid = request.forms.get('pid').strip()
    pname = request.forms.get('pname')
    product = Product(id=pid, pname=pname, instock='Pending')
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
    rdate = ndb.DateTimeProperty(auto_now=True)

def send_mail(pid, pname):
    message = mail.EmailMessage(sender='noreply@istockcheck.appspotmail.com',
                                subject='Back in Stock Notification')
    message.to = 'jchen@live.it'
    message.body = '''
    Your Product is back in stock now:
    {pname}
    <a href="http://www.microsoftstore.com/store/msusa/en_US/pdp/productID.{pid}">Click</a>
    '''.format(pid=pid, pname=pname)
    message.send()

