import { Link } from 'react-router-dom';
import { Box, ArrowRight, Zap, Shield, BarChart3 } from 'lucide-react';
import './Home.css';

const GeometricBackground = () => {
  const points = [
    [0,0], [8,0], [20,0], [45,0], [100,0],
    [0,12], [10,14], [25,10], [50,15], [100,18],
    [0,30], [15,35], [32,30], [60,35], [100,32],
    [0,60], [20,65], [42,55], [75,60], [100,65],
    [0,100], [25,100], [55,100], [80,100], [100,100]
  ];

  const triangles = [];
  for (let j = 0; j < 4; j++) {
    for (let i = 0; i < 4; i++) {
      const p1 = points[j * 5 + i];
      const p2 = points[j * 5 + i + 1];
      const p3 = points[(j + 1) * 5 + i];
      const p4 = points[(j + 1) * 5 + i + 1];

      if ((i + j) % 2 === 0) {
        triangles.push(`${p1[0]},${p1[1]} ${p2[0]},${p2[1]} ${p4[0]},${p4[1]}`);
        triangles.push(`${p1[0]},${p1[1]} ${p4[0]},${p4[1]} ${p3[0]},${p3[1]}`);
      } else {
        triangles.push(`${p1[0]},${p1[1]} ${p2[0]},${p2[1]} ${p3[0]},${p3[1]}`);
        triangles.push(`${p2[0]},${p2[1]} ${p4[0]},${p4[1]} ${p3[0]},${p3[1]}`);
      }
    }
  }

  return (
    <svg 
      className="geometric-bg" 
      viewBox="0 0 100 100" 
      preserveAspectRatio="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {triangles.map((pts, idx) => {
        const opacity = (idx * 13 % 10) * 0.005 + 0.02; // Increased opacity for aesthetics
        return (
          <polygon 
            key={idx} 
            points={pts} 
            fill={`rgba(212, 175, 55, ${opacity})`} 
            stroke="#050505" 
            strokeWidth="0.3" 
            className="mesh-triangle"
          />
        );
      })}
    </svg>
  );
};

const Home = () => {
  return (
    <div className="home-container animate-fade-in">
      {/* Ambient Background Elements */}
      <div className="ambient-orb orb-1"></div>
      <div className="ambient-orb orb-2"></div>
      <div className="ambient-orb orb-3"></div>
      
      {/* Geometric Triangles */}
      <GeometricBackground />

      {/* Navigation */}
      <nav className="home-nav">
        <div className="home-logo">
          <Box className="home-logo-icon" size={28} />
          <span>Nexus</span>
        </div>
        <div className="home-nav-links">
          <Link to="/login" className="nav-link">Log In</Link>
          <Link to="/register" className="btn-glass">Get Started</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="hero-section">
        <h1 className="hero-title animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <span className="text-gradient">Production </span>
          <span className="text-accent-gradient">Manager</span>
        </h1>

        <p className="hero-subtitle animate-slide-up" style={{ animationDelay: '0.3s' }}>
          Streamline your inventory, empower your team, and scale your business with our cutting-edge, high-performance platform built for modern enterprises.
        </p>

        <div className="hero-actions animate-slide-up" style={{ animationDelay: '0.4s' }}>
          <Link to="/login" className="btn-outline-lg">
            Log In <ArrowRight size={18} />
          </Link>
          <Link to="/register" className="btn-accent btn-lg">
            Start for free
          </Link>
        </div>

        {/* Features Preview */}
        <div className="features-preview animate-slide-up" style={{ animationDelay: '0.5s' }}>
          <div className="feature-card">
            <div className="feature-icon-wrapper" style={{ background: 'rgba(212, 175, 55, 0.1)', color: '#D4AF37' }}>
              <Zap size={24} />
            </div>
            <h3>Lightning Fast</h3>
            <p>Experience zero-latency operations with our optimized global edge infrastructure and highly responsive interface.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper" style={{ background: 'rgba(192, 192, 192, 0.1)', color: '#C0C0C0' }}>
              <Shield size={24} />
            </div>
            <h3>Enterprise Security</h3>
            <p>Your data is protected by military-grade encryption and strictly enforced role-based access controls.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper" style={{ background: 'rgba(212, 175, 55, 0.1)', color: '#D4AF37' }}>
              <BarChart3 size={24} />
            </div>
            <h3>Real-time Analytics</h3>
            <p>Make data-driven decisions instantly with live inventory tracking, rich metrics, and dynamic dashboards.</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home;
