import React from 'react';
import AccountDetails from '../components/AccountDetails';

const Settings = () => {
    return (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <h1 className="text-3xl font-bold text-slate-900 mb-8">Settings</h1>
            <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
                <AccountDetails />
            </div>
        </div>
    );
};

export default Settings;
