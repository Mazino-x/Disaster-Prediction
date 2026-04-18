import './Features.css';
import { Link } from 'react-router-dom';

const FEATURES = [
  {
    to: '/location',
    className: 'featureLocation',
    icon: '📍',
    name: 'Location Risk Assessment',
    desc: 'Click any point on the map to instantly get earthquake & tsunami risk scores for that area.',
  },
  {
    to: '/earthquake',
    className: 'feature1',
    icon: '🌋',
    name: 'Earthquake Prediction',
    desc: 'Enter coordinates, depth, and date to predict seismic activity magnitude risk.',
  },
  {
    to: '/tsunami',
    className: 'feature3',
    icon: '🌊',
    name: 'Tsunami Prediction',
    desc: 'Provide seismic parameters to assess the probability of a tsunami event.',
  },
];

function Features() {
  return (
    <div className="featuresContainer">
      {FEATURES.map((f, i) => (
        <Link key={f.to} to={f.to} className={`feature ${f.className}`} style={{ animationDelay: `${i * 0.1 + 0.1}s` }}>
          <span className="featureIcon">{f.icon}</span>
          <h3 className="featureName">{f.name}</h3>
          <p className="featureDesc">{f.desc}</p>
          <span className="featureCta">Get started →</span>
        </Link>
      ))}
    </div>
  );
}

export default Features;
