import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Disaster Predictor app with features', () => {
  render(<App />);
  const titleElement = screen.getByText(/Disaster Predictor/i);
  expect(titleElement).toBeInTheDocument();
  
  // Check that key features are rendered
  const earthquakeFeature = screen.getByText(/Earthquake Prediction/i);
  expect(earthquakeFeature).toBeInTheDocument();
  
  const tsunamiFeature = screen.getByText(/Tsunami Prediction/i);
  expect(tsunamiFeature).toBeInTheDocument();
  
  const locationFeature = screen.getByText(/Location-Based Risk Assessment/i);
  expect(locationFeature).toBeInTheDocument();
});
