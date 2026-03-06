import api from '../api';

const notificationsService = {
    getNotifications: async () => {
        const response = await api.get('/notifications/');
        return response.data;
    },

    markAsRead: async (id) => {
        const response = await api.post(`/notifications/${id}/read`);
        return response.data;
    }
};

export default notificationsService;
