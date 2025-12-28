"""
Playwright with remote ZAP proxy on a server
"""
import os, time, json

from zapv2 import ZAPv2
from datetime import datetime
from playwright.sync_api import sync_playwright

from har import parse
from database import main    as sqlite_db
from database import queries as sqlite_queries


#
# Global Variables
#
ZAP_SERVER_IP = "172.17.0.2"#"192.168.29.129"
ZAP_PORT      = "8080"

ZAP_PROXY     = f"http://{ZAP_SERVER_IP}:{ZAP_PORT}"
ZAP_API_KEY   = "S3CR3T"

SQLITE_PATH   = "data/database.db"


def stamp(): 
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def connect_zap() -> ZAPv2:
    """
    Establishe a connection to remote instance of OWASP ZAP.

    Returns:
        ZAPv2: An instance of the ZAPv2 client connected to the specified proxy,
                or 
               None if the connection fails.
    """
    global ZAP_PROXY
    global ZAP_API_KEY
    
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
    
    return zap


def visit( url : str ):
    """
    """
    
    print(f"[{stamp()}][{__name__}][✈] Using Playwright to navigate to { url } ...")
    
    #
    #   Open with Playwright,
    #
    with sync_playwright() as p:
        
        # Initialize
        browser   = p.chromium.launch( headless = False )
        context   = browser.new_context(
            proxy = {
                "server" : ZAP_PROXY,
            },
            ignore_https_errors = True
        )
        
        # Navigate to the page
        page = context.new_page()
        page.goto( url )
        page.wait_for_load_state('networkidle')
        
        # Done! 
        print(f"[{stamp()}][{__name__}][✓] Page loaded. ")
        time.sleep(2); browser.close()
        
        
def export_data( zap : ZAPv2 ):
    """
    """
    print(f"[{stamp()}][{__name__}][✈] Exporting data from the ZAP instance '{ZAP_SERVER_IP}' ...")
    
    # Get data from remote instance
    urls = zap.core.urls()
    har  = zap.core.messages_har()

    print(f"[{stamp()}][{__name__}][✈] Writing data to cache/ ...")
    
    # Write data to disk
    if not os.path.isdir("cache"): os.makedirs("cache")
    
    with open("cache/remote_zap_urls.txt", "w+") as f:
        for _url in urls: f.write(_url + "\n")

    with open("cache/remote_zap_traffic.har", "w") as f: 
        f.write(har)
    
    
    
def parse_data():
    with open("cache/remote_zap_traffic.har", "r") as file:
        data    = json.loads(file.read())
        objects = parse.contents_from_json( data )
        return objects    
    
    
#
#   Main Flow
#
def main( url ):
    """
    """
    
    #
    #   Initialization phase
    #
    
    sql_database_required_tables = {
        "ZapHistoryEntries" : sqlite_queries.create_zap_history_table,
        "ZapCookies"        : sqlite_queries.create_zap_cookies, 
        "ZapHeaders"        : sqlite_queries.create_zap_headers
    }
    sqlite_db.initialize_db( sql_database_required_tables, SQLITE_PATH )
    
    
    #
    # start a new session
    #
    zap = connect_zap()
    zap.core.new_session(name="clean_session", overwrite=True)
    
    #
    # Visit the site
    #
    visit( url )
    
    #
    # Export data from remote ZAP
    #
    export_data( zap )
    print(f"[{stamp()}][{__name__}][✓] All data exported from remote ZAP instance {ZAP_SERVER_IP} for { url }")
    
    
    #
    #   Parse data
    #
    print(f"[{stamp()}][{__name__}][✈] Parsing data for { url } ...")
    
    for object in parse_data():
        url, status, text, encoding, created_at = object["url"], object["status"], object["text"], object["encoding"], stamp()
        
        row = sqlite_db.insert_data(
            sqlite_queries.insert_into_zap_history,
            (url, status, text, encoding, created_at)
        )
        
    print(f"[{stamp()}][{__name__}][✓] Done! Pushed into database")
    
if __name__ == '__main__':
    #
    #   Main entry
    #
    main( "https://wtfismyip.com/" )
    