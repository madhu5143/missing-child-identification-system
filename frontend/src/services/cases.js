import api from '../api';

const casesService = {
    getAllCases: async (skip = 0, limit = 100, search = '', status = '') => {
        let query = `/cases/?skip=${skip}&limit=${limit}`;
        if (search) query += `&search=${encodeURIComponent(search)}`;
        if (status && status !== 'All') query += `&status=${encodeURIComponent(status)}`;

        const response = await api.get(query);
        return response.data;
    },

    getCaseById: async (id) => {
        const response = await api.get(`/cases/${id}`);
        return response.data;
    },

    createCase: async (caseData) => {
        // specific for multipart/form-data or simple json? 
        // Backend `create_missing_person` uses Form(...) 
        // So we need to send FormData if we want to match exactly, 
        // OR we can send JSON if we change backend to accept Pydantic model.
        // The backend `create_missing_person` signature:
        // full_name: str = Form(...), ...

        const formData = new FormData();
        for (const key in caseData) {
            formData.append(key, caseData[key]);
        }

        console.log("Sending createCase request with token:", localStorage.getItem('token'));
        try {
            // Let Axios handle the Content-Type header (it adds the boundary automatically for FormData)
            const response = await api.post('/cases/', formData);
            return response.data;
        } catch (error) {
            console.error("createCase failed:", error.response?.status, error.response?.data);
            throw error;
        }
    },

    updateCase: async (id, caseUpdate) => {
        const response = await api.put(`/cases/${id}`, caseUpdate);
        return response.data;
    },

    deleteCase: async (id) => {
        await api.delete(`/cases/${id}`);
    },

    uploadCaseImages: async (id, filesArray) => {
        const formData = new FormData();
        filesArray.forEach(file => {
            formData.append('files', file);
        });
        // Let Axios handle the Content-Type header
        const response = await api.post(`/cases/${id}/images`, formData);
        return response.data;
    },

    resolveCase: async (id) => {
        const response = await api.post(`/cases/${id}/resolve`);
        return response.data;
    },

    getCaseStats: async () => {
        const response = await api.get('/cases/stats');
        return response.data;
    },

    getCaseMatches: async (caseId) => {
        const response = await api.get(`/cases/${caseId}/matches`);
        return response.data;
    },

    reviewMatch: async (matchId, status) => {
        const formData = new FormData();
        formData.append('status', status);
        const response = await api.post(`/cases/matches/${matchId}/review`, formData);
        return response.data;
    }
};

export default casesService;
