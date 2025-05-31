import React, { useEffect, useRef, memo } from 'react';

function TradingViewWidget() {
  const container = useRef();
  const scriptAdded = useRef(false); // Flaga, aby upewnić się, że skrypt jest dodawany tylko raz

  useEffect(() => {
    if (scriptAdded.current) return; // Jeśli skrypt został już dodany, zakończ

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.innerHTML = `
      {
        "autosize": true,
        "symbol": "NASDAQ:AAPL",
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
    scriptAdded.current = true; // Ustaw flagę, aby zapobiec wielokrotnemu dodawaniu skryptu
  }, []);

  return (
    <div className="tradingview-widget-container" ref={container} style={{ height: "122%", width: "100%" }}>
      <div className="tradingview-widget-container__widget" style={{ height: "calc(100% - 32px)", width: "100%" }}></div>
      {/*
      <div className="tradingview-widget-copyright">
        <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
          <span className="blue-text">Track all markets on TradingView</span>
        </a>
      </div>
      */}
    </div>
  );
}

export default memo(TradingViewWidget);
