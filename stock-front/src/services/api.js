import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Envoie un message au chatbot
 * @param {string} message - Le message de l'utilisateur
 * @returns {Promise} Réponse du chatbot
 */
export const sendMessage = async (message) => {
  try {
    const response = await api.post('/chat', { message });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.message || 'Erreur serveur');
    } else if (error.request) {
      throw new Error('Impossible de contacter le serveur. Vérifiez que le backend est lancé.');
    } else {
      throw new Error('Erreur inattendue: ' + error.message);
    }
  }
};

/**
 * Upload un fichier Excel
 * @param {File} file - Le fichier Excel à uploader
 * @returns {Promise} Résultat de l'upload
 */
export const uploadFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.message || "Erreur lors de l'upload");
    } else if (error.request) {
      throw new Error('Impossible de contacter le serveur.');
    } else {
      throw new Error('Erreur inattendue: ' + error.message);
    }
  }
};

/**
 * Vérifie la santé du serveur
 * @returns {Promise} Status du serveur
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Le serveur ne répond pas.');
  }
};

export default api;
