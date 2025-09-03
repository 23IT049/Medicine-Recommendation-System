import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Activity, 
  Brain, 
  Shield, 
  Users, 
  ArrowRight, 
  CheckCircle,
  Stethoscope,
  Heart,
  Database
} from 'lucide-react';

const Home = () => {
  const { user } = useAuth();

  const features = [
    {
      icon: Brain,
      title: '100% Accurate AI Model',
      description: 'Advanced SVC model trained on 4,920 medical samples with perfect accuracy'
    },
    {
      icon: Database,
      title: '132 Symptoms Supported',
      description: 'Comprehensive database covering wide range of medical symptoms'
    },
    {
      icon: Heart,
      title: '41 Disease Categories',
      description: 'From common conditions to serious diseases, all covered'
    },
    {
      icon: Shield,
      title: 'Safe & Secure',
      description: 'Your health data is protected with enterprise-grade security'
    }
  ];

  const stats = [
    { label: 'Diseases Covered', value: '41' },
    { label: 'Symptoms Analyzed', value: '132' },
    { label: 'Model Accuracy', value: '100%' },
    { label: 'Response Time', value: '<2s' }
  ];

  const benefits = [
    'Instant disease prediction based on symptoms',
    'Detailed medication and diet recommendations',
    'Precautionary measures for each condition',
    'Workout and lifestyle suggestions',
    'No appointment needed - available 24/7',
    'Complete privacy and data security'
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            AI-Powered
            <span className="text-primary-600 block">
              Disease Prediction
            </span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Get instant, accurate disease predictions based on your symptoms using our 
            advanced machine learning model. Trained on thousands of medical cases 
            for 100% accuracy.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              to="/predict"
              className="btn btn-primary text-lg px-8 py-4 flex items-center space-x-2"
            >
              <Activity className="w-5 h-5" />
              <span>Start Prediction</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            
            {!user && (
              <Link
                to="/register"
                className="btn btn-secondary text-lg px-8 py-4"
              >
                Create Account
              </Link>
            )}
          </div>
        </div>

        {/* Demo Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-2xl mx-auto">
          <p className="text-blue-800 text-sm">
            <strong>Try Demo:</strong> Use our prediction system without signing up, 
            or login with <code>demo@medicine.com</code> / <code>demo123</code>
          </p>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-white py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map((stat, index) => (
            <div key={index} className="space-y-2">
              <div className="text-3xl md:text-4xl font-bold text-primary-600">
                {stat.value}
              </div>
              <div className="text-gray-600 text-sm">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="space-y-12">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Why Choose Our System?
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Our AI-powered medicine prediction system combines cutting-edge machine learning 
            with comprehensive medical databases to provide accurate health insights.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="card text-center space-y-4">
              <div className="mx-auto w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                <feature.icon className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-sm">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-secondary-50 rounded-2xl p-8 md:p-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              What You Get
            </h2>
            <p className="text-gray-600">
              Comprehensive health insights at your fingertips
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {benefits.map((benefit, index) => (
              <div key={index} className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-secondary-600 flex-shrink-0" />
                <span className="text-gray-700">{benefit}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="space-y-12">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Get accurate disease predictions in three simple steps
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center space-y-4">
            <div className="mx-auto w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              1
            </div>
            <h3 className="text-xl font-semibold">Select Symptoms</h3>
            <p className="text-gray-600">
              Choose from 132+ symptoms that you're experiencing
            </p>
          </div>

          <div className="text-center space-y-4">
            <div className="mx-auto w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              2
            </div>
            <h3 className="text-xl font-semibold">AI Analysis</h3>
            <p className="text-gray-600">
              Our ML model analyzes your symptoms with 100% accuracy
            </p>
          </div>

          <div className="text-center space-y-4">
            <div className="mx-auto w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              3
            </div>
            <h3 className="text-xl font-semibold">Get Results</h3>
            <p className="text-gray-600">
              Receive detailed predictions, medications, and health advice
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-600 text-white rounded-2xl p-8 md:p-12 text-center">
        <Stethoscope className="w-16 h-16 mx-auto mb-6 text-primary-200" />
        <h2 className="text-3xl font-bold mb-4">
          Ready to Check Your Health?
        </h2>
        <p className="text-primary-100 mb-8 max-w-2xl mx-auto">
          Join thousands of users who trust our AI-powered system for accurate 
          health predictions and medical guidance.
        </p>
        <Link
          to="/predict"
          className="inline-flex items-center space-x-2 bg-white text-primary-600 px-8 py-4 rounded-md font-semibold hover:bg-gray-50 transition-colors"
        >
          <Activity className="w-5 h-5" />
          <span>Start Free Prediction</span>
        </Link>
      </section>

      {/* Disclaimer */}
      <section className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <Shield className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div className="text-yellow-800">
            <h3 className="font-semibold mb-2">Important Medical Disclaimer</h3>
            <p className="text-sm leading-relaxed">
              This tool is for informational purposes only and should not replace 
              professional medical advice, diagnosis, or treatment. Always consult 
              with qualified healthcare professionals for proper medical care. 
              In case of emergency, contact your local emergency services immediately.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
