import time, json
from flask import Blueprint, jsonify, request

from zapv2 import ZAPv2
from datetime import datetime
from playwright.sync_api import sync_playwright

from har import parse
from database import main    as sqlite_db
from database import queries as sqlite_queries


api = Blueprint("api", __name__, url_prefix="/api")

#
# Global Variables
#
ZAP_SERVER_IP = "localhost"#"192.168.29.129"
ZAP_PORT      = "8080"

ZAP_PROXY     = f"http://{ZAP_SERVER_IP}:{ZAP_PORT}"
ZAP_API_KEY   = "S3CR3T"

ZAP_INSTANCE  : ZAPv2 = None  


#
#   Implementation
#
def stamp(): 
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def connect_zap() -> ZAPv2:
    """
    Establishes a connection to remote instance of OWASP ZAP.

    Returns:
        ZAPv2: An instance of the ZAPv2 client connected to the specified proxy,
                or 
               None if the connection fails.
    """
    global ZAP_PROXY
    global ZAP_API_KEY
    global ZAP_INSTANCE
    
    print(f"[{stamp()}][{__name__}][✈] Connecting to ZAP at {ZAP_PROXY} ...")
    
    zap = ZAPv2(
        apikey  = ZAP_API_KEY,
        proxies = { "http"  : ZAP_PROXY, "https" : ZAP_PROXY }
    )
    
    try:
        version = zap.core.version
        print(f"[{stamp()}][{__name__}][✓] Connected to remote ZAP version: {version}")
        
    except Exception as e:
        print(f"[{stamp()}][{__name__}][✗] Error connecting to ZAP: {e}")
        return None
    
    ZAP_INSTANCE = zap
    return zap


def export_data( zap : ZAPv2 ):
    """
    Export data from a ZAP instance into cache.
    """
    print(f"[{stamp()}][{__name__}][✈] Exporting data from the ZAP instance '{ZAP_SERVER_IP}' ...")
    
    if zap == None:
        print(f"[{stamp()}][{__name__}][✈] Not connected to a ZAP instance. Trying to connect to: '{ZAP_SERVER_IP}' ...")
        zap = connect_zap()
    
    # Get data from remote instance
    urls = zap.core.urls()
    har  = zap.core.messages_har()

    print(f"[{stamp()}][{__name__}][✈] Writing data to cache/ ...")
    
    # Write data to disk
    with open("cache/remote_zap_urls.txt", "w+") as f:
        for _url in urls: f.write(_url + "\n")

    with open("cache/remote_zap_traffic.har", "w") as f: 
        f.write(har)
    

def parse_data( url ):
    objects = []
    with open("cache/remote_zap_traffic.har", "r") as file:
        data    = json.loads(file.read())
        objects = parse.contents_from_json( data )
            
    print(f"[{stamp()}][{__name__}][✈] Parsing data for { url } ...")
    
    if objects == []:
        print(f"[{stamp()}][{__name__}][!] received no data? ")    
        return
    
    for object in objects:
        url, status, text, encoding, created_at = object["url"], object["status"], object["text"], object["encoding"], stamp()
        
        row = sqlite_db.insert_data(
            sqlite_queries.insert_into_zap_history,
            (url, status, text, encoding, created_at)
        )
        
        print( row )

#
#   Routes
#
@api.route( "/status" )
def status():
    return "200"


@api.route( "/visit/<url>"  )
@api.route( "/visit/<url>/" )
def visit( url ):
    global ZAP_INSTANCE
    
    if ZAP_INSTANCE == None:
        ZAP_INSTANCE = connect_zap()
        
    ZAP_INSTANCE.core.new_session(name="clean_session", overwrite=True)
    
    print(f"[{stamp()}][{__name__}][✈] Using Playwright to navigate to { url } ...")
    
    #
    #   Open with Playwright,
    #
    with sync_playwright() as p:
        
        # Initialize
        browser   = p.chromium.launch( headless = True, args=["--no-sandbox"] )
        context   = browser.new_context(
            proxy = {
                "server" : ZAP_PROXY,
            },
            ignore_https_errors = True
        )
        
        # Navigate to the page
        page = context.new_page()
        page.goto( "http://" + url )
        page.wait_for_load_state('networkidle')
        
        # Done! 
        print(f"[{stamp()}][{__name__}][✓] Page loaded. ")
        time.sleep(2); browser.close()
    
    export_data( ZAP_INSTANCE )
    parse_data( url )
    return "200"


@api.route( "/fetch/<url>"  )
@api.route( "/fetch/<url>/" )
def fetch( url ):
    
    data = []
    
    rows = sqlite_db.query_database( sqlite_queries.select_zap_history_by_url, (url,) )
    for row in rows:
        url, status, text, encoding, created_at = row[0], row[1], row[2], row[3], row[4]
        data.append({
            "url"         : url,
            "status"      : status,
            "text"        : text,
            "encoding"    : encoding,
            "created_at"  : created_at
        })
         
    return jsonify( data )