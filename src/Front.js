import './Front.css';
import Features from './Features';

function Front() {
  return (
    <div className="frontContainer">
      <div className="heroSection">
        <div className="heroBadge">AI-Powered Early Warning System</div>
        <h1 className="heroTitle">Predict Natural Disasters<br />Before They Strike</h1>
        <p className="heroSubtitle">
          Machine learning models trained on historical seismic & tsunami data
          help assess risk for any location on Earth.
        </p>
      </div>
      <Features />
      <footer className="homeFooter">
        <p>For educational purposes only &nbsp;·&nbsp; Always consult official warning agencies for safety decisions</p>
      </footer>
    </div>
  );
}

export default Front;
