<template>
  <div class="container">
    <section class="hero">
      <h1>Welcome to AI Travel Planner</h1>
      <p class="hero-subtitle">
        Plan your perfect trip with AI-powered itinerary generation and smart expense tracking
      </p>
      <div class="hero-actions">
        <router-link to="/itineraries/create" class="btn btn-primary">
          Start Planning Your Trip
        </router-link>
        <router-link to="/itineraries" class="btn btn-secondary">
          View My Itineraries
        </router-link>
      </div>
    </section>

    <section class="features">
      <h2>Features</h2>
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">🤖</div>
          <h3>AI-Powered Itineraries</h3>
          <p>
            Generate personalized travel plans based on your preferences, budget, and dates using
            advanced AI models (Qwen/Doubao).
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">💰</div>
          <h3>Expense Tracking</h3>
          <p>
            Track your travel expenses by category and compare against your planned budget in
            real-time.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🗺️</div>
          <h3>Smart Navigation</h3>
          <p>
            Integrated with Amap for accurate location search and route planning with multiple
            transport modes.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🎤</div>
          <h3>Voice Input</h3>
          <p>
            Use voice commands powered by iFlytek to quickly add expenses or search for
            destinations.
          </p>
        </div>
      </div>
    </section>

    <section class="how-it-works">
      <h2>How It Works</h2>
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <h3>Enter Your Preferences</h3>
          <p>Tell us where you want to go, when, and what you like to do</p>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <h3>Get AI-Generated Itinerary</h3>
          <p>Receive a personalized day-by-day plan with activities and costs</p>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <h3>Track Your Expenses</h3>
          <p>Log expenses during your trip and stay within budget</p>
        </div>
        <div class="step">
          <div class="step-number">4</div>
          <h3>Enjoy Your Trip!</h3>
          <p>Follow your plan and make amazing memories</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  text-align: center;
  padding: 4rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.features {
  margin-bottom: 4rem;
}

.features h2 {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #2c3e50;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  color: #667eea;
  margin-bottom: 0.75rem;
}

.how-it-works {
  margin-bottom: 4rem;
}

.how-it-works h2 {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #2c3e50;
}

.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.step {
  text-align: center;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 auto 1rem;
}

.step h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.step p {
  color: #6c757d;
}
</style>
