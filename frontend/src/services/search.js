import api from '../api';

const searchService = {
    searchFace: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/search/', formData);
        return response.data;
    }
};

export default searchService;
