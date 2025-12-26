FROM zaproxy/zap-stable

USER root

# Install Tor and Proxychains
RUN apt-get update && \
    apt-get install -y tor proxychains-ng && \
    rm -rf /var/lib/apt/lists/*

# Install Chromium runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    wget \
    xdg-utils \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


RUN apt-get install python3 python3-pip -y

COPY . .

# Install Python dependencies + playwright
RUN pip install -r requirements.txt --break-system-packages
RUN playwright install chromium

# Configure Tor
RUN echo "SOCKSPort 9050" >> /etc/tor/torrc && \
    echo "Log notice stdout" >> /etc/tor/torrc

# Configure proxychains
RUN echo "\
strict_chain\n\
proxy_dns\n\
[ProxyList]\n\
socks5 127.0.0.1 9050\n\
" > /etc/proxychains.conf

# Start Tor, then ZAP (daemon mode, routed via Tor)
CMD tor & \
    python3 app.py & \
    proxychains zap.sh \
      -daemon \
      -host 0.0.0.0 \
      -port 8080 \
      -config api.addrs.addr.name=.* \
      -config api.addrs.addr.regex=true \
      -config api.key="S3CR3T" 
      