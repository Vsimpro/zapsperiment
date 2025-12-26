"""
*
*   Type: SQLite
*
"""


#
#   Queries for storing data from Zap .har's
#
create_zap_history_table = """
CREATE TABLE IF NOT EXISTS ZapHistoryEntry (
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    url        TEXT     NOT NULL,
    status     INTEGER  NOT NULL,
    text       TEXT     NOT NULL,
    encoding   TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

insert_into_zap_history = """
INSERT INTO ZapHistoryEntry (
    url, 
    status, 
    text, 
    encoding, 
    created_at
)
VALUES (?, ?, ?, ?, ?);
"""
"""url, status, text, encoding, created_at"""

select_zap_history_by_url = """
SELECT url, status, text, encoding, created_at FROM ZapHistoryEntry WHERE url LIKE '%' || ? || '%'
"""
"""url, status, text, encoding, created_at"""

#
#   Zap cookies
#
create_zap_cookies = """
CREATE TABLE IF NOT EXISTS ZapCookies (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL, -- Which ZapHistoryEntry this metadata is tied to
    
    cookies  TEXT    NOT NULL, -- Cookies as JSON
    
    FOREIGN KEY(entry_id) REFERENCES ZapHistoryEntry(id) ON DELETE CASCADE
);
"""


#
#   Zap headers
#
create_zap_headers = """
CREATE TABLE IF NOT EXISTS ZapHeaders (
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL, -- Which ZapHistoryEntry this metadata is tied to
    
    headers  TEXT    NOT NULL, -- Headers as JSON 
    
    FOREIGN KEY(entry_id) REFERENCES ZapHistoryEntry(id) ON DELETE CASCADE
);
"""