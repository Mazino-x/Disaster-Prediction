import './Front.css';
import Features from './Features';

function Front() {
    return (
        <div className="frontContainer">
            <nav className="navbar">
                <p className="navbarHeading">Disaster Predictor</p>
            </nav>
            <Features />
        </div>
    );
}

export default Front;