import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, ShieldCheck, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Home = () => {
    const { user } = useAuth();

    return (
        <div className="bg-white">
            {/* Hero Section */}
            <div className="relative overflow-hidden bg-slate-900 text-white">
                <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80')] bg-cover bg-center opacity-20"></div>
                <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="text-center"
                    >
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
                            Reuniting Families with <span className="text-indigo-400">Advanced AI</span>
                        </h1>
                        <p className="max-w-2xl mx-auto text-xl text-gray-300 mb-10">
                            Our Next-Generation Identification System uses state-of-the-art Deep Learning to match missing children with reported sightings instantly.
                        </p>
                        <div className="flex justify-center flex-wrap gap-4 mt-8">
                            <Link to="/search" className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-full font-bold text-lg transition-all shadow-lg hover:shadow-indigo-500/30">
                                Search Database
                            </Link>
                            {user ? (
                                <Link to={user.role === 'admin' ? "/admin" : "/dashboard"} className="bg-slate-700 hover:bg-slate-600 text-white px-8 py-4 rounded-full font-bold text-lg transition-all">
                                    {user.role === 'admin' ? 'Admin Dashboard' : 'Dashboard'}
                                </Link>
                            ) : (
                                <>
                                    <Link to="/login?role=admin" className="bg-slate-700 hover:bg-slate-600 text-white px-8 py-4 rounded-full font-bold text-lg transition-all">
                                        Login as Admin
                                    </Link>
                                    <Link to="/login?role=sub_admin" className="bg-slate-700 hover:bg-slate-600 text-white px-8 py-4 rounded-full font-bold text-lg transition-all">
                                        Login as Sub-admin
                                    </Link>
                                </>
                            )}
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Features Section */}
            <div className="py-24 bg-slate-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold text-slate-900">Why Choose Our System?</h2>
                        <p className="mt-4 text-slate-600">Built for accuracy, speed, and privacy.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        <FeatureCard
                            icon={<Search className="h-10 w-10 text-indigo-600" />}
                            title="Deep Learning Logic"
                            description="Utilizes VGG-Face/ResNet models for high-accuracy face matching even with aging or partial occlusion."
                        />
                        <FeatureCard
                            icon={<ShieldCheck className="h-10 w-10 text-indigo-600" />}
                            title="Secure & Private"
                            description="Role-based access control and secure data handling to ensure sensitive information stays protected."
                        />
                        <FeatureCard
                            icon={<Users className="h-10 w-10 text-indigo-600" />}
                            title="User Friendly"
                            description="Simple drag-and-drop interface designed for law enforcement and the general public."
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

const FeatureCard = ({ icon, title, description }) => (
    <motion.div
        whileHover={{ y: -5 }}
        className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100"
    >
        <div className="mb-4 bg-indigo-50 w-16 h-16 rounded-xl flex items-center justify-center">
            {icon}
        </div>
        <h3 className="text-xl font-semibold mb-2 text-slate-900">{title}</h3>
        <p className="text-slate-600 leading-relaxed">{description}</p>
    </motion.div>
);

export default Home;
