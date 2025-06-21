import React from 'react';

const GeckoTerminalWidget = () => (
  <div style={{ width: '100%', height: '100%', minHeight: 400 }}>
    <iframe
      height="100%"
      width="100%"
      id="geckoterminal-embed"
      title="GeckoTerminal Embed"
      src="https://www.geckoterminal.com/pl/solana/pools/HLNwfTqQbmrPaQEfQ3z8f78obevHumhY1BB6UrLKjyXd?embed=1&info=1&swaps=1&grayscale=0&light_chart=0&chart_type=price&resolution=15m"
      frameBorder="0"
      allow="clipboard-write"
      allowFullScreen
      style={{ border: 0, borderRadius: 12, minHeight: 400 }}
    ></iframe>
  </div>
);

export default GeckoTerminalWidget;