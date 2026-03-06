import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import authService from '../services/auth';
import { Users, Mail, Phone, User as UserIcon } from 'lucide-react';

const SubAdminsList = () => {
    const { user } = useAuth();
    const [subAdmins, setSubAdmins] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (user && user.role === 'admin') {
            fetchSubAdmins();
        }
    }, [user]);

    const fetchSubAdmins = async () => {
        try {
            setLoading(true);
            const data = await authService.getSubAdmins();
            setSubAdmins(data);
            setError(null);
        } catch (err) {
            console.error("Failed to fetch sub-admins", err);
            setError("Failed to load sub-admins. Please try again later.");
        } finally {
            setLoading(false);
        }
    };

    if (!user || user.role !== 'admin') {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-red-600 font-medium">Access Denied. Admins only.</div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 h-full min-h-screen">
            <div className="md:flex md:items-center md:justify-between mb-6">
                <div className="flex-1 min-w-0">
                    <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate flex items-center gap-2">
                        <Users className="h-8 w-8 text-indigo-600" />
                        Registered Sub-admins
                    </h2>
                </div>
            </div>

            {error && (
                <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-md shadow-sm border border-red-100">
                    {error}
                </div>
            )}

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                    Name
                                </th>
                                <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                    Username
                                </th>
                                <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                    Email
                                </th>
                                <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                    Phone Number
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {loading ? (
                                <tr>
                                    <td colSpan="4" className="px-6 py-12 text-center text-gray-500">
                                        Loading sub-admins...
                                    </td>
                                </tr>
                            ) : subAdmins.length === 0 ? (
                                <tr>
                                    <td colSpan="4" className="px-6 py-12 text-center text-gray-500">
                                        No sub-admins found in the system.
                                    </td>
                                </tr>
                            ) : (
                                subAdmins.map((subAdmin) => (
                                    <tr key={subAdmin.id} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center bg-indigo-100 rounded-full">
                                                    <span className="text-indigo-700 font-semibold text-lg">
                                                        {subAdmin.username.charAt(0).toUpperCase()}
                                                    </span>
                                                </div>
                                                <div className="ml-4">
                                                    {/* We only have username right now based on the model, so we display it here too, or a placeholder if a true "name" field is ever added */}
                                                    <div className="text-sm font-medium text-gray-900 border-b border-dashed border-gray-300 pb-0.5 inline-block">
                                                        {subAdmin.username} User
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center text-sm text-gray-600">
                                                <UserIcon className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                                                {subAdmin.username}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center text-sm text-gray-600">
                                                <Mail className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                                                {subAdmin.email || <span className="text-gray-400 italic">Not provided</span>}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center text-sm text-gray-600">
                                                <Phone className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                                                {subAdmin.mobile_number || <span className="text-gray-400 italic">Not provided</span>}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default SubAdminsList;
