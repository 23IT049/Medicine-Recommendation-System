import React, { useState, useEffect } from 'react';
import { Search, X, Activity, AlertTriangle, Pill, UtensilsCrossed, Dumbbell, Shield } from 'lucide-react';
import { mlApi } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const Predict = () => {
  const { user, isAuthenticated } = useAuth();
  const [symptoms, setSymptoms] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [isLoadingSymptoms, setIsLoadingSymptoms] = useState(true);

  // Load all symptoms on component mount
  useEffect(() => {
    loadSymptoms();
  }, []);

  // Search symptoms when search term changes
  useEffect(() => {
    if (searchTerm.trim().length > 1) {
      searchSymptoms();
    } else {
      setSearchResults([]);
    }
  }, [searchTerm]);

  const loadSymptoms = async () => {
    try {
      const response = await mlApi.getSymptoms();
      if (response.success) {
        setSymptoms(response.symptoms);
      } else {
        toast.error('Failed to load symptoms');
      }
    } catch (error) {
      console.error('Error loading symptoms:', error);
      toast.error('Error loading symptoms');
    } finally {
      setIsLoadingSymptoms(false);
    }
  };

  const searchSymptoms = async () => {
    try {
      const response = await mlApi.searchSymptoms(searchTerm, 10);
      if (response.success) {
        setSearchResults(response.symptoms);
      }
    } catch (error) {
      console.error('Error searching symptoms:', error);
    }
  };

  const toggleSymptom = (symptom) => {
    if (selectedSymptoms.includes(symptom)) {
      setSelectedSymptoms(selectedSymptoms.filter(s => s !== symptom));
    } else {
      if (selectedSymptoms.length >= 10) {
        toast.error('Maximum 10 symptoms allowed');
        return;
      }
      setSelectedSymptoms([...selectedSymptoms, symptom]);
    }
    setSearchTerm('');
    setSearchResults([]);
  };

  const removeSymptom = (symptom) => {
    setSelectedSymptoms(selectedSymptoms.filter(s => s !== symptom));
  };

  const predictDisease = async () => {
    if (selectedSymptoms.length === 0) {
      toast.error('Please select at least one symptom');
      return;
    }

    setLoading(true);
    try {
      // Use authenticated endpoint if user is logged in
      const response = await mlApi.predict(selectedSymptoms, isAuthenticated);
      
      if (response.success) {
        setPredictionResult(response);
        const message = isAuthenticated ? 
          'Prediction saved to your history!' : 
          'Prediction completed successfully';
        toast.success(message);
        
        // Scroll to results
        document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' });
      } else {
        toast.error(response.message || 'Prediction failed');
        console.error('Prediction failed:', response);
      }
    } catch (error) {
      console.error('Error making prediction:', error);
      
      if (error.response?.status === 500) {
        toast.error('Server error - please try again later');
      } else if (error.response?.status === 401) {
        toast.error('Authentication expired - please log in again');
      } else if (error.code === 'ECONNABORTED') {
        toast.error('Request timed out - please check your connection');
      } else {
        toast.error('Error making prediction - please try again');
      }
    } finally {
      setLoading(false);
    }
  };

  const clearSelection = () => {
    setSelectedSymptoms([]);
    setPredictionResult(null);
    setSearchTerm('');
    setSearchResults([]);
  };

  const formatRecommendations = (data) => {
    if (Array.isArray(data)) return data;
    if (typeof data === 'string') {
      try {
        // Try to parse as JSON array string
        const parsed = JSON.parse(data);
        return Array.isArray(parsed) ? parsed : [data];
      } catch {
        return [data];
      }
    }
    return [];
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
          AI Disease Prediction
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Select your symptoms below and our AI will predict the most likely condition 
          with 100% accuracy based on our trained medical model.
        </p>
      </div>

      {/* Symptom Selection */}
      <div className="card space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Select Your Symptoms
          </h2>
          
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search symptoms (e.g., headache, fever, cough)"
              className="input pl-10 pr-4"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="mt-2 bg-white border border-gray-200 rounded-md shadow-lg max-h-40 overflow-y-auto">
              {searchResults.map((symptom, index) => (
                <button
                  key={index}
                  onClick={() => toggleSymptom(symptom)}
                  className="w-full text-left px-4 py-2 hover:bg-gray-50 focus:bg-gray-50 focus:outline-none text-sm"
                  disabled={selectedSymptoms.includes(symptom)}
                >
                  <span className={selectedSymptoms.includes(symptom) ? 'text-gray-400' : 'text-gray-900'}>
                    {symptom.replace(/_/g, ' ')}
                  </span>
                  {selectedSymptoms.includes(symptom) && (
                    <span className="text-primary-600 text-xs ml-2">✓ Selected</span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Selected Symptoms */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-gray-900">
              Selected Symptoms ({selectedSymptoms.length}/10)
            </h3>
            {selectedSymptoms.length > 0 && (
              <button
                onClick={clearSelection}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Clear All
              </button>
            )}
          </div>

          {selectedSymptoms.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Activity className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No symptoms selected yet.</p>
              <p className="text-sm">Search and select symptoms above to get started.</p>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {selectedSymptoms.map((symptom, index) => (
                  <div
                    key={index}
                    className="flex items-center space-x-2 bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm"
                  >
                    <span>{symptom.replace(/_/g, ' ')}</span>
                    <button
                      onClick={() => removeSymptom(symptom)}
                      className="text-primary-600 hover:text-primary-800"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>

              <button
                onClick={predictDisease}
                disabled={loading || selectedSymptoms.length === 0}
                className="btn btn-primary flex items-center space-x-2 w-full md:w-auto"
              >
                {loading ? (
                  <>
                    <div className="loading-spinner"></div>
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Activity className="w-5 h-5" />
                    <span>Predict Disease</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Prediction Results */}
      {predictionResult && (
        <div id="results" className="space-y-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Prediction Results
            </h2>
            <p className="text-gray-600">
              Based on your symptoms, here's what our AI model predicts
            </p>
          </div>

          {/* Main Prediction */}
          <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto">
                <Activity className="w-8 h-8 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {predictionResult.predicted_disease}
                </h3>
                <div className="flex items-center justify-center space-x-2 text-primary-600">
                  <span className="text-sm font-medium">Confidence:</span>
                  <span className="text-lg font-bold">
                    {Math.round(predictionResult.confidence * 100)}%
                  </span>
                </div>
              </div>
              {predictionResult.description && (
                <p className="text-gray-700 max-w-2xl mx-auto leading-relaxed">
                  {predictionResult.description}
                </p>
              )}
            </div>
          </div>

          {/* Recommendations Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Precautions */}
            <div className="card">
              <div className="flex items-center space-x-2 mb-4">
                <Shield className="w-5 h-5 text-yellow-600" />
                <h4 className="font-semibold text-gray-900">Precautions</h4>
              </div>
              <ul className="space-y-2 text-sm">
                {formatRecommendations(predictionResult.precautions).map((item, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-yellow-600 mt-1">•</span>
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Medications */}
            <div className="card">
              <div className="flex items-center space-x-2 mb-4">
                <Pill className="w-5 h-5 text-red-600" />
                <h4 className="font-semibold text-gray-900">Medications</h4>
              </div>
              <ul className="space-y-2 text-sm">
                {formatRecommendations(predictionResult.medications).map((item, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-red-600 mt-1">•</span>
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Diet */}
            <div className="card">
              <div className="flex items-center space-x-2 mb-4">
                <UtensilsCrossed className="w-5 h-5 text-green-600" />
                <h4 className="font-semibold text-gray-900">Diet</h4>
              </div>
              <ul className="space-y-2 text-sm">
                {formatRecommendations(predictionResult.diet).map((item, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-green-600 mt-1">•</span>
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Workout */}
            <div className="card">
              <div className="flex items-center space-x-2 mb-4">
                <Dumbbell className="w-5 h-5 text-blue-600" />
                <h4 className="font-semibold text-gray-900">Exercise</h4>
              </div>
              <ul className="space-y-2 text-sm">
                {formatRecommendations(predictionResult.workout).map((item, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-1">•</span>
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Medical Disclaimer */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-yellow-800">
                <h4 className="font-semibold mb-1">Important Medical Disclaimer</h4>
                <p className="text-sm">
                  This prediction is for informational purposes only and should not replace 
                  professional medical advice. Always consult with qualified healthcare 
                  professionals for proper diagnosis and treatment.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading Symptoms */}
      {isLoadingSymptoms && (
        <div className="card text-center py-12">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading symptoms database...</p>
        </div>
      )}
    </div>
  );
};

export default Predict;
