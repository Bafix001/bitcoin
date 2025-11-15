import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [latestPrices, setLatestPrices] = useState([]);
  const [bestPrices, setBestPrices] = useState([]);
  const [arbitrage, setArbitrage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [latest, best, arb] = await Promise.all([
          axios.get('http://localhost:8000/prices/latest'),
          axios.get('http://localhost:8000/prices/best'),
          axios.get('http://localhost:8000/prices/arbitrage')
        ]);
        
        setLatestPrices(latest.data.data || []);
        setBestPrices(best.data.data || []);
        setArbitrage(arb.data.data);
        setLoading(false);
      } catch (error) {
        console.error('Erreur:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="loading">Chargement des données</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Bitcoin Price Comparator</h1>
        <p>Comparaison en temps réel des prix sur plusieurs exchanges</p>
      </header>

      {arbitrage && arbitrage.profit > 0 && (
        <div className="arbitrage-alert">
          <h2>Opportunité d'Arbitrage</h2>
          <p>
            Acheter sur <strong>{arbitrage.buy_exchange}</strong> à ${parseFloat(arbitrage.buy_price).toFixed(2)}
            <br />
            Vendre sur <strong>{arbitrage.sell_exchange}</strong> à ${parseFloat(arbitrage.sell_price).toFixed(2)}
            <br />
            <span className="profit">
              Profit: ${parseFloat(arbitrage.profit).toFixed(2)} ({parseFloat(arbitrage.profit_percentage).toFixed(3)}%)
            </span>
          </p>
        </div>
      )}

      <div className="prices-container">
        <h2>Prix en temps réel</h2>
        <div className="cards">
          {latestPrices.map((item, index) => (
            <div key={index} className="price-card">
              <h3>{item.exchange.toUpperCase()}</h3>
              <p className="price">${parseFloat(item.price).toFixed(2)}</p>
              <p className="time">{new Date(item.datetime).toLocaleTimeString()}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="best-prices">
        <h2>Meilleurs prix</h2>
        <table>
          <thead>
            <tr>
              <th>Exchange</th>
              <th>Meilleur achat</th>
              <th>Meilleur vente</th>
              <th>Prix moyen</th>
              <th>Trades</th>
            </tr>
          </thead>
          <tbody>
            {bestPrices.map((item, index) => (
              <tr key={index}>
                <td><strong>{item.exchange.toUpperCase()}</strong></td>
                <td className="buy">${parseFloat(item.best_buy_price).toFixed(2)}</td>
                <td className="sell">${parseFloat(item.best_sell_price).toFixed(2)}</td>
                <td>${parseFloat(item.avg_price).toFixed(2)}</td>
                <td>{item.trade_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
