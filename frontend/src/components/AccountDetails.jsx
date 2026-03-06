import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import authService from '../services/auth';
import { Settings, Phone, Key, Lock, Check, User as UserIcon, Mail, ShieldAlert } from 'lucide-react';

const AccountDetails = () => {
    const { user } = useAuth();

    // Profile State
    const [profile, setProfile] = useState({ username: '', email: '', mobile_number: '' });
    const [profileLoading, setProfileLoading] = useState(false);
    const [profileMessage, setProfileMessage] = useState('');
    const [profileError, setProfileError] = useState('');

    // Password Change State
    const [step, setStep] = useState(1); // 1: Form, 2: Success
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [passLoading, setPassLoading] = useState(false);
    const [passMessage, setPassMessage] = useState('');
    const [passError, setPassError] = useState('');

    useEffect(() => {
        if (user && (user.role === 'sub_admin' || user.role === 'admin')) {
            fetchProfile();
        }
    }, [user]);

    const fetchProfile = async () => {
        try {
            const data = await authService.getProfile();
            setProfile({ username: data.username, email: data.email, mobile_number: data.mobile_number || '' });
        } catch (err) {
            console.error("Failed to load profile", err);
        }
    };

    if (!user || (user.role !== 'sub_admin' && user.role !== 'admin')) {
        return null;
    }

    const handleProfileUpdate = async (e) => {
        e.preventDefault();
        setProfileLoading(true);
        setProfileError('');
        setProfileMessage('');

        try {
            // Include username but backend only updates email/mobile intentionally.
            await authService.updateProfile({
                email: profile.email,
                mobile_number: profile.mobile_number
            });
            setProfileMessage('Profile updated successfully!');
        } catch (err) {
            setProfileError(err.response?.data?.detail || 'Failed to update profile.');
        } finally {
            setProfileLoading(false);
        }
    };

    const handleChangePassword = async (e) => {
        e.preventDefault();

        if (newPassword !== confirmPassword) {
            setPassError("New passwords do not match.");
            return;
        }

        setPassLoading(true);
        setPassError('');
        setPassMessage('');

        try {
            await authService.changePassword(oldPassword, newPassword);
            setPassMessage('Password changed successfully!');
            setStep(2); // Success state
        } catch (err) {
            setPassError(err.response?.data?.detail || 'Failed to change password. Please check your old password.');
        } finally {
            setPassLoading(false);
        }
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Profile Section */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                    <UserIcon className="h-5 w-5 text-indigo-600" />
                    Profile Information
                </h2>

                {profileMessage && <div className="mb-4 p-3 bg-green-50 text-green-700 rounded-md text-sm">{profileMessage}</div>}
                {profileError && <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">{profileError}</div>}

                <form onSubmit={handleProfileUpdate} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Username (Read-only)</label>
                        <div className="relative">
                            <UserIcon className="absolute top-2.5 left-3 h-4 w-4 text-gray-400" />
                            <input
                                type="text"
                                value={profile.username}
                                disabled
                                className="w-full pl-9 pr-3 py-2 bg-gray-50 border border-gray-200 rounded-md text-gray-500 text-sm cursor-not-allowed"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                        <div className="relative">
                            <Mail className="absolute top-2.5 left-3 h-4 w-4 text-gray-400" />
                            <input
                                required
                                type="email"
                                value={profile.email}
                                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 text-sm"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Registered Mobile Number</label>
                        <div className="relative">
                            <Phone className="absolute top-2.5 left-3 h-4 w-4 text-gray-400" />
                            <input
                                required
                                type="tel"
                                value={profile.mobile_number}
                                onChange={(e) => setProfile({ ...profile, mobile_number: e.target.value })}
                                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 text-sm"
                            />
                        </div>
                    </div>
                    <button
                        type="submit"
                        disabled={profileLoading}
                        className="w-full bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors disabled:opacity-70 mt-2"
                    >
                        {profileLoading ? 'Saving...' : 'Save Profile Changes'}
                    </button>
                </form>
            </div>

            {/* Password Reset Section */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                    <ShieldAlert className="h-5 w-5 text-indigo-600" />
                    Security & Password
                </h2>

                {passMessage && <div className="mb-4 p-3 bg-green-50 text-green-700 rounded-md text-sm">{passMessage}</div>}
                {passError && <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">{passError}</div>}

                {step === 1 && (
                    <form onSubmit={handleChangePassword} className="space-y-4">
                        <p className="text-sm text-gray-600 mb-4">Change your account password by providing your current password.</p>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Old Password</label>
                            <div className="relative">
                                <Key className="absolute top-2.5 left-3 h-4 w-4 text-gray-400" />
                                <input
                                    required
                                    type="password"
                                    value={oldPassword}
                                    onChange={(e) => setOldPassword(e.target.value)}
                                    className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 text-sm"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                            <div className="relative">
                                <Lock className="absolute top-2.5 left-3 h-4 w-4 text-gray-400" />
                                <input
                                    required
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 text-sm"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                            <div className="relative">
                                <Lock className="absolute top-2.5 left-3 h-4 w-4 text-gray-400" />
                                <input
                                    required
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 text-sm"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>
                        <button
                            type="submit"
                            disabled={passLoading}
                            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors disabled:opacity-70 mt-2"
                        >
                            {passLoading ? 'Updating Password...' : 'Change Password'}
                        </button>
                    </form>
                )}

                {step === 2 && (
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
                        <div className="bg-green-100 p-2 rounded-full flex-shrink-0">
                            <Check className="h-5 w-5 text-green-600" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-green-800">Password Changed</h3>
                            <p className="text-sm text-green-600">You may now use your new password next time you login.</p>
                            <button
                                onClick={() => { setStep(1); setOldPassword(''); setNewPassword(''); setConfirmPassword(''); setPassMessage(''); }}
                                className="mt-2 text-sm text-indigo-600 hover:underline font-medium"
                            >
                                Change again
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AccountDetails;

