import React, { useState, useEffect } from 'react';
import notificationsService from '../services/notifications';
import { Bell, Check, Clock, AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const NotificationCenter = () => {
    const { user } = useAuth();
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAll, setShowAll] = useState(false);

    useEffect(() => {
        fetchNotifications();
        const interval = setInterval(fetchNotifications, 30000); // Poll every 30s
        return () => clearInterval(interval);
    }, []);

    const fetchNotifications = async () => {
        try {
            const data = await notificationsService.getNotifications();
            setNotifications(data);
        } catch (error) {
            console.error("Failed to fetch notifications");
        } finally {
            setLoading(false);
        }
    };

    const markAsRead = async (id) => {
        try {
            await notificationsService.markAsRead(id);
            setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: 1 } : n));
        } catch (error) {
            console.error("Failed to mark notification as read");
        }
    };

    const unreadCount = notifications.filter(n => !n.is_read).length;

    // Filter displayed notifications based on toggle
    const displayedNotifications = showAll
        ? notifications
        : notifications.filter(n => !n.is_read);

    if (loading && notifications.length === 0) return null;

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-8">
            <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <Bell className={`h-5 w-5 ${unreadCount > 0 ? 'text-red-500 fill-red-500' : 'text-slate-400'}`} />
                    <h2 className="font-bold text-slate-800">
                        {user?.role === 'admin' ? 'Admin Notifications' : 'My Notifications'}
                    </h2>
                    {unreadCount > 0 && (
                        <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                            {unreadCount} NEW
                        </span>
                    )}
                </div>
                <div className="flex gap-4 items-center">
                    <button
                        onClick={() => setShowAll(!showAll)}
                        className="text-xs text-slate-500 hover:text-indigo-600 font-medium"
                    >
                        {showAll ? 'Hide Read' : 'View History'}
                    </button>
                    <button onClick={fetchNotifications} className="text-xs text-indigo-600 hover:underline font-medium">Refresh</button>
                </div>
            </div>

            <div className="max-h-60 overflow-y-auto">
                {displayedNotifications.length === 0 ? (
                    <div className="p-8 text-center text-slate-400 text-sm">
                        {showAll ? 'No notifications history.' : 'No new notifications.'}
                    </div>
                ) : (
                    displayedNotifications.map((n) => (
                        <div key={n.id} className={`p-4 border-b border-slate-50 flex gap-4 items-start transition-colors ${!n.is_read ? 'bg-indigo-50/30' : 'bg-white'}`}>
                            <div className={`p-2 rounded-lg shrink-0 ${n.type === 'match_found' ? 'bg-amber-100 text-amber-600' : 'bg-blue-100 text-blue-600'}`}>
                                <AlertTriangle className="h-4 w-4" />
                            </div>
                            <div className="flex-1">
                                <p className={`text-sm ${!n.is_read ? 'font-semibold text-slate-900' : 'text-slate-600'}`}>
                                    {n.message}
                                </p>
                                <div className="flex items-center gap-3 mt-1">
                                    <span className="text-[10px] flex items-center gap-1 text-slate-400">
                                        <Clock className="h-3 w-3" />
                                        {new Date(n.created_at).toLocaleString()}
                                    </span>
                                    {!n.is_read && (
                                        <button
                                            onClick={() => markAsRead(n.id)}
                                            className="text-[10px] font-bold text-indigo-600 hover:text-indigo-800 uppercase tracking-wider"
                                        >
                                            Mark as Read
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default NotificationCenter;
