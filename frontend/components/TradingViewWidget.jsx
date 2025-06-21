import React, { useEffect, useRef, memo } from 'react';
import GeckoTerminalWidget from '@/components/GeckoTerminalWidget';

function TradingViewWidget({ useGecko = true, symbol = "NASDAQ:AAPL" }) {
  const container = useRef();
  const scriptAdded = useRef(false);

  useEffect(() => {
    if (useGecko) return;
    if (scriptAdded.current) return;

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.innerHTML = `
      {
        "autosize": true,
        "symbol": "${symbol}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "support_host": "https://www.tradingview.com"
      }`;
    container.current.appendChild(script);
    scriptAdded.current = true;
  }, [useGecko, symbol]);

  if (useGecko) {
    return <GeckoTerminalWidget />;
  }

  return (
    <div className="tradingview-widget-container" ref={container} style={{ height: "90%", width: "100%" }}>
      <div className="tradingview-widget-container__widget" style={{ height: "100%", width: "100%" }}></div>
    </div>
  );
}

export default memo(TradingViewWidget);