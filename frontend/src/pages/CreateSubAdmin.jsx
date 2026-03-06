import React from 'react';
import SubAdminForm from '../components/SubAdminForm';

const CreateSubAdmin = () => {
    return (
        <div className="max-w-4xl mx-auto px-4 py-8 h-full min-h-screen">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Create New Sub-admin</h1>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                <SubAdminForm />
            </div>
        </div>
    );
};

export default CreateSubAdmin;
