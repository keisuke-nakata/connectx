import React from 'react';
import { TreeDataReader } from './features/tree/TreeDataReader';
import { TreeViz } from './features/tree/TreeViz';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <TreeViz />
        <TreeDataReader />
      </header>
    </div>
  );
}

export default App;
