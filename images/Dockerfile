FROM zaproxy/zap-stable

USER root

# Install Tor
RUN apt-get update && \
    apt-get install -y tor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configure Tor
RUN echo "SOCKSPort 9050" >> /etc/tor/torrc && \
    echo "Log notice stdout" >> /etc/tor/torrc

# Expose ZAP API port
EXPOSE 8090

# Start Tor, then ZAP (daemon mode, routed via Tor)
CMD tor & \
    zap.sh \
      -daemon \
      -host 0.0.0.0 \
      -port 8090 \
      -config connection.proxyChain.enabled=true \
      -config connection.proxyChain.host=0.0.0.0 \
      -config connection.proxyChain.port=9050 \
      -config connection.proxyChain.type=SOCKS5 \
      -config connection.proxyChain.dns=true \
      -config api.addrs.addr.name=.* \
      -config api.addrs.addr.regex=true \
      -config api.key="S3CR3T"
      