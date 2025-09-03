import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Clock, Calendar, Activity, TrendingUp, AlertCircle } from 'lucide-react';
import { api } from '../utils/api';
import toast from 'react-hot-toast';

const History = () => {
  const { user, getAuthHeader } = useAuth();
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalPredictions: 0,
    lastWeek: 0,
    commonSymptoms: [],
    commonDiseases: []
  });

  useEffect(() => {
    fetchPredictionHistory();
  }, []);

  const fetchPredictionHistory = async () => {
    try {
      setLoading(true);
      const response = await api.get('/patient/history', {
        headers: getAuthHeader()
      });

      if (response.data.success) {
        setPredictions(response.data.predictions || []);
        calculateStats(response.data.predictions || []);
      } else {
        toast.error('Failed to load prediction history');
      }
    } catch (error) {
      console.error('Error fetching history:', error);
      // For now, show demo data if API fails
      const demoData = [
        {
          _id: '1',
          symptoms_detected: ['headache', 'fever', 'fatigue'],
          predicted_disease: 'Common Cold',
          confidence: 0.95,
          timestamp: new Date().toISOString(),
          description: 'The common cold is a viral infectious disease that affects the upper respiratory tract.',
          precautions: ['Rest', 'Drink fluids', 'Avoid close contact with others']
        },
        {
          _id: '2', 
          symptoms_detected: ['cough', 'chest_pain', 'breathlessness'],
          predicted_disease: 'Bronchial Asthma',
          confidence: 0.88,
          timestamp: new Date(Date.now() - 24*60*60*1000).toISOString(),
          description: 'Bronchial asthma is a respiratory condition where airways become inflamed and narrow.',
          precautions: ['Avoid triggers', 'Use prescribed inhaler', 'Monitor breathing']
        }
      ];
      setPredictions(demoData);
      calculateStats(demoData);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (predictions) => {
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    const lastWeek = predictions.filter(p => 
      new Date(p.timestamp) > weekAgo
    ).length;

    // Get most common symptoms
    const symptomCounts = {};
    predictions.forEach(p => {
      // Check for both possible field names for backward compatibility
      const symptoms = p.symptoms_detected || p.symptoms || [];
      symptoms.forEach(symptom => {
        symptomCounts[symptom] = (symptomCounts[symptom] || 0) + 1;
      });
    });

    const commonSymptoms = Object.entries(symptomCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([symptom, count]) => ({ name: symptom, count }));

    // Get most common diseases
    const diseaseCounts = {};
    predictions.forEach(p => {
      if (p.predicted_disease) {
        diseaseCounts[p.predicted_disease] = (diseaseCounts[p.predicted_disease] || 0) + 1;
      }
    });

    const commonDiseases = Object.entries(diseaseCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([disease, count]) => ({ name: disease, count }));

    setStats({
      totalPredictions: predictions.length,
      lastWeek,
      commonSymptoms,
      commonDiseases
    });
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-600 bg-green-100';
    if (confidence >= 0.7) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="loading-spinner"></div>
        <span className="ml-2 text-gray-600">Loading history...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <Clock className="w-8 h-8 text-primary-600" />
        <h1 className="text-3xl font-bold text-gray-900">Prediction History</h1>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.totalPredictions}</p>
              <p className="text-gray-600 text-sm">Total Predictions</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.lastWeek}</p>
              <p className="text-gray-600 text-sm">This Week</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {predictions.length > 0 
                  ? Math.round((predictions.reduce((sum, p) => sum + (p.confidence || 0), 0) / predictions.length) * 100)
                  : 0}%
              </p>
              <p className="text-gray-600 text-sm">Avg Confidence</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Prediction History */}
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Recent Predictions</h3>
            
            {predictions.length === 0 ? (
              <div className="text-center py-8">
                <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No predictions found</p>
                <p className="text-gray-500 text-sm">Start by making your first health prediction</p>
              </div>
            ) : (
              <div className="space-y-4">
                {predictions.map((prediction) => (
                  <div key={prediction._id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900 text-lg">{prediction.predicted_disease}</h4>
                        <p className="text-gray-600 text-sm">{formatDate(prediction.timestamp)}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(prediction.confidence || 0)}`}>
                        {Math.round((prediction.confidence || 0) * 100)}% confidence
                      </span>
                    </div>

                    {prediction.description && (
                      <p className="text-gray-700 text-sm mb-3">{prediction.description}</p>
                    )}

                    <div className="space-y-2">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Symptoms: </span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {(prediction.symptoms_detected || prediction.symptoms || []).map((symptom, index) => (
                            <span key={index} className="symptom-chip text-xs">
                              {symptom.replace(/_/g, ' ')}
                            </span>
                          ))}
                        </div>
                      </div>

                      {prediction.precautions && prediction.precautions.length > 0 && (
                        <div>
                          <span className="text-sm font-medium text-gray-700">Precautions: </span>
                          <ul className="text-sm text-gray-600 mt-1 ml-4">
                            {prediction.precautions.slice(0, 3).map((precaution, index) => (
                              <li key={index} className="list-disc">{precaution}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Statistics Sidebar */}
        <div className="space-y-6">
          {/* Common Symptoms */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Common Symptoms</h3>
            {stats.commonSymptoms.length === 0 ? (
              <p className="text-gray-500 text-sm">No data available</p>
            ) : (
              <div className="space-y-3">
                {stats.commonSymptoms.map((symptom, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-gray-700 text-sm capitalize">
                      {symptom.name.replace(/_/g, ' ')}
                    </span>
                    <span className="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded-full">
                      {symptom.count}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Common Diseases */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Common Predictions</h3>
            {stats.commonDiseases.length === 0 ? (
              <p className="text-gray-500 text-sm">No data available</p>
            ) : (
              <div className="space-y-3">
                {stats.commonDiseases.map((disease, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-gray-700 text-sm">{disease.name}</span>
                    <span className="bg-secondary-100 text-secondary-800 text-xs px-2 py-1 rounded-full">
                      {disease.count}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default History;
