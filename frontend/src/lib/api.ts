/**
 * API Utilities for Smart Flashcard AI Backend
 * Handles all communication with the Flask backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Store auth token
export const setAuthToken = (token: string) => {
  localStorage.setItem('authToken', token);
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken');
};

export const clearAuthToken = () => {
  localStorage.removeItem('authToken');
};

// Helper function for authenticated API calls
async function apiCall(endpoint: string, options: RequestInit = {}) {
  const token = getAuthToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid
      clearAuthToken();
      window.location.href = '/auth';
    }
    
    const error = await response.json();
    throw new Error(error.error || `API Error: ${response.status}`);
  }
  
  return response.json();
}

async function fileApiCall(endpoint: string, formData: FormData) {
  const token = getAuthToken();
  const headers: HeadersInit = {};
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/auth';
    }
    
    const error = await response.json();
    throw new Error(error.error || `API Error: ${response.status}`);
  }
  
  return response.json();
}

// Authentication API calls
export const authAPI = {
  signup: async (email: string, password: string, name: string) => {
    const data = await apiCall('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
    setAuthToken(data.token);
    return data;
  },
  
  login: async (email: string, password: string) => {
    const data = await apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setAuthToken(data.token);
    return data;
  },
  
  getProfile: async () => {
    return apiCall('/auth/profile');
  },
  
  updateProfile: async (name: string) => {
    return apiCall('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify({ name }),
    });
  },
  
  changePassword: async (oldPassword: string, newPassword: string) => {
    return apiCall('/auth/change-password', {
      method: 'PUT',
      body: JSON.stringify({ oldPassword, newPassword }),
    });
  },
};

// Flashcard API calls
export const flashcardAPI = {
  generate: async (text: string, title: string) => {
    return apiCall('/generate', {
      method: 'POST',
      body: JSON.stringify({ text, title }),
    });
  },
  
  generateFromFile: async (file: File, title: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    return fileApiCall('/generate', formData);
  },
  
  getAll: async (skip = 0, limit = 50, filters: Record<string, any> = {}) => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
      ...filters,
    });
    return apiCall(`/flashcards?${params}`);
  },
  
  get: async (id: string) => {
    return apiCall(`/flashcards/${id}`);
  },
  
  markKnown: async (id: string, known: boolean) => {
    return apiCall(`/flashcards/${id}/known`, {
      method: 'PUT',
      body: JSON.stringify({ known }),
    });
  },
  
  addToFavorites: async (id: string) => {
    return apiCall(`/flashcards/${id}/favorite`, {
      method: 'POST',
    });
  },
  
  removeFromFavorites: async (id: string) => {
    return apiCall(`/flashcards/${id}/favorite`, {
      method: 'DELETE',
    });
  },
  
  delete: async (id: string) => {
    return apiCall(`/flashcards/${id}`, {
      method: 'DELETE',
    });
  },
  
  getFavorites: async (skip = 0, limit = 50) => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    return apiCall(`/favorites?${params}`);
  },
};

// History API calls
export const historyAPI = {
  getAll: async (skip = 0, limit = 50, search?: string, topic?: string, subject?: string) => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (search) params.append('search', search);
    if (topic) params.append('topic', topic);
    else if (subject) params.append('subject', subject);
    return apiCall(`/history?${params}`);
  },
  
  get: async (id: string) => {
    return apiCall(`/history/${id}`);
  },
  
  update: async (id: string, title: string) => {
    return apiCall(`/history/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ title }),
    });
  },
  
  delete: async (id: string) => {
    return apiCall(`/history/${id}`, {
      method: 'DELETE',
    });
  },
  
  getSubjects: async () => {
    return apiCall('/history/subjects');
  },
  
  getTopics: async () => {
    return apiCall('/history/topics');
  },
};

// Statistics API calls
export const statisticsAPI = {
  getDashboard: async () => {
    return apiCall('/statistics');
  },
  
  getBySubject: async (subject: string) => {
    return apiCall(`/statistics/subject/${encodeURIComponent(subject)}`);
  },
};

// Export API calls
export const exportAPI = {
  asJSON: async (noteId?: string) => {
    const params = new URLSearchParams();
    if (noteId) params.append('noteId', noteId);
    return apiCall(`/export/json?${params}`);
  },
  
  asCSV: async (noteId?: string) => {
    const params = new URLSearchParams();
    if (noteId) params.append('noteId', noteId);
    const response = await fetch(`${API_BASE_URL}/export/csv?${params}`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });
    if (!response.ok) throw new Error('Export failed');
    return response.blob();
  },
  
  getPDFData: async (noteId?: string) => {
    const params = new URLSearchParams();
    if (noteId) params.append('noteId', noteId);
    return apiCall(`/export/pdf-data?${params}`);
  },
};

// Settings API calls
export const settingsAPI = {
  get: async () => {
    return apiCall('/settings');
  },
  
  update: async (fullName: string) => {
    return apiCall('/settings', {
      method: 'PUT',
      body: JSON.stringify({ fullName }),
    });
  },
};

// Health check
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
};

export default {
  authAPI,
  flashcardAPI,
  historyAPI,
  statisticsAPI,
  exportAPI,
  settingsAPI,
  healthCheck,
};
