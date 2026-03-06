import api from '../api';

const authService = {
    login: async (username, password) => {
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);
        const response = await api.post('/auth/token', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        return response.data;
    },

    createSubAdmin: async (userData) => {
        const response = await api.post('/auth/create-subadmin', userData);
        return response.data;
    },

    requestOtp: async (mobile_number) => {
        const response = await api.post('/auth/request-otp', { mobile_number });
        return response.data;
    },

    resetPassword: async (mobile_number, otp, new_password) => {
        const response = await api.post('/auth/reset-password', { mobile_number, otp, new_password });
        return response.data;
    },

    changePassword: async (old_password, new_password) => {
        const response = await api.post('/auth/change-password', { old_password, new_password });
        return response.data;
    },

    getSubAdmins: async () => {
        const response = await api.get('/auth/sub-admins');
        return response.data;
    },

    getProfile: async () => {
        const response = await api.get('/auth/me');
        return response.data;
    },

    updateProfile: async (userData) => {
        const response = await api.put('/auth/me', userData);
        return response.data;
    },

    getSystemStatus: async () => {
        const response = await api.get('/api/status');
        return response.data;
    }
};

export default authService;
