import React, { useState, useEffect } from 'react';
import casesService from '../services/cases';
import FileUploader from '../components/FileUploader';
import { Loader2, Plus, AlertCircle, Edit2, Trash2, X, Search } from 'lucide-react';
import NotificationCenter from '../components/NotificationCenter';
import MatchReviewModal from '../components/MatchReviewModal';

const Dashboard = () => {
    const [cases, setCases] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        full_name: '',
        age: '',
        gender: 'Male',
        state: '',
        district: '',
        last_seen_location: '',
        parent_contact_number: '',
        station_name: '',
        station_address: '',
        station_contact_number: '',
        description: '',
    });
    const [selectedImages, setSelectedImages] = useState([]);
    const [submitLoading, setSubmitLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [editingCase, setEditingCase] = useState(null);
    const [viewingCase, setViewingCase] = useState(null);
    const [reviewingMatchesCase, setReviewingMatchesCase] = useState(null);

    // Filter & Pagination State
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('All');
    const [page, setPage] = useState(0);
    const LIMIT = 9; // Display 9 cards per page

    const [stats, setStats] = useState({ total_cases: 0, missing_count: 0, found_count: 0 });

    useEffect(() => {
        // Debounce search
        const delayDebounceFn = setTimeout(() => {
            fetchCases();
        }, 500);

        return () => clearTimeout(delayDebounceFn);
    }, [searchQuery, statusFilter, page]);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchCases = async () => {
        setLoading(true);
        try {
            const skip = page * LIMIT;
            const data = await casesService.getAllCases(skip, LIMIT, searchQuery, statusFilter);
            setCases(data);
        } catch (error) {
            console.error("Failed to fetch cases");
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const data = await casesService.getCaseStats();
            setStats(data);
        } catch (error) {
            console.error("Failed to fetch stats");
        }
    };

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!editingCase && selectedImages.length < 3) {
            setMessage('Please select at least 3 clear photos of the child. This is required for accurate AI analysis.');
            return;
        }
        setSubmitLoading(true);
        setMessage('');

        try {
            if (editingCase) {
                // Update existing case
                await casesService.updateCase(editingCase.id, formData);
                setMessage('Case updated successfully!');
            } else {
                // Create New Case
                // casesService.createCase expects object, not FormData if we updated it to handle it?
                // Wait, in my implementation plan I wrote createCase to take caseData and convert to FormData.
                // But here we are already creating FormData.
                // Let's adjust Dashboard to pass plain object and let Service handle FormData conversion.

                const caseData = await casesService.createCase(formData);
                const caseId = caseData.id;

                // 2. Upload Images
                await casesService.uploadCaseImages(caseId, selectedImages);
                setMessage('Case reported successfully!');
            }

            setShowForm(false);
            resetForm();
            fetchCases();
            fetchStats();
        } catch (error) {
            console.error(error);
            let errorMsg = error.response?.data?.detail;

            if (Array.isArray(errorMsg)) {
                // Handle FastAPI validation error list
                errorMsg = errorMsg.map(err => `${err.loc.join('.')}: ${err.msg}`).join(' | ');
            } else if (typeof errorMsg === 'object' && errorMsg !== null) {
                errorMsg = JSON.stringify(errorMsg);
            }

            errorMsg = errorMsg || `Failed to ${editingCase ? 'update' : 'create'} case.`;
            setMessage(`${errorMsg} Please try again.`);
        } finally {
            setSubmitLoading(false);
        }
    };

    const resetForm = () => {
        setFormData({
            full_name: '',
            age: '',
            gender: 'Male',
            state: '',
            district: '',
            last_seen_location: '',
            parent_contact_number: '',
            station_name: '',
            station_address: '',
            station_contact_number: '',
            description: '',
            status: 'missing'
        });
        setSelectedImages([]);
        setEditingCase(null);
    };

    const handleEdit = (c) => {
        setEditingCase(c);
        setFormData({
            full_name: c.full_name,
            age: c.age,
            gender: c.gender,
            state: c.state || '',
            district: c.district || '',
            last_seen_location: c.last_seen_location,
            parent_contact_number: c.parent_contact_number || c.contact_phone || '',
            station_name: c.station_name || '',
            station_address: c.station_address || '',
            station_contact_number: c.station_contact_number || '',
            description: c.description || '',
            status: c.status
        });
        setShowForm(true);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleView = async (caseId) => {
        try {
            const caseData = await casesService.getCaseById(caseId);
            setViewingCase(caseData);
        } catch (error) {
            alert("Failed to fetch full case details.");
        }
    };

    const handleDelete = async (caseId) => {
        if (window.confirm('Are you sure you want to delete this case? This action cannot be undone.')) {
            try {
                await casesService.deleteCase(caseId);
                setMessage('Case deleted successfully');
                fetchCases();
                fetchStats();
            } catch (error) {
                console.error("Delete failed", error);
                alert("Failed to delete case");
            }
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
                <button
                    onClick={() => setShowForm(!showForm)}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md flex items-center gap-2"
                >
                    <Plus className="h-5 w-5" /> Report Missing Child
                </button>
            </div>

            <div className="mb-8">
                <NotificationCenter />
            </div>

            {showForm && (
                <div className="bg-white p-6 rounded-lg shadow-md mb-8 border border-gray-200">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-semibold">{editingCase ? 'Edit Case Details' : 'Report New Case'}</h2>
                        <button onClick={() => { setShowForm(false); resetForm(); }} className="text-gray-400 hover:text-gray-600">
                            <X className="h-6 w-6" />
                        </button>
                    </div>
                    {message && <div className={`mb-4 p-3 rounded ${message.includes('success') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{message}</div>}
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                            <input required name="full_name" type="text" value={formData.full_name} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
                            <input required name="age" type="number" value={formData.age} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                            <select name="gender" value={formData.gender} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border">
                                <option>Male</option>
                                <option>Female</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                            <input required name="state" type="text" value={formData.state} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">District</label>
                            <input required name="district" type="text" value={formData.district} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Last Seen Location</label>
                            <input required name="last_seen_location" type="text" value={formData.last_seen_location} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Parent Contact Number</label>
                            <input required name="parent_contact_number" type="tel" value={formData.parent_contact_number} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Station Name</label>
                            <input required name="station_name" type="text" value={formData.station_name} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Station Address</label>
                            <input required name="station_address" type="text" value={formData.station_address} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Station Contact</label>
                            <input required name="station_contact_number" type="tel" value={formData.station_contact_number} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" />
                        </div>
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                            <textarea name="description" value={formData.description} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" rows="3"></textarea>
                        </div>
                        {editingCase && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                                <select name="status" value={formData.status} onChange={handleInputChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border">
                                    <option value="missing">Missing</option>
                                    <option value="found">Found</option>
                                </select>
                            </div>
                        )}
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-2">{editingCase ? 'Update Photo (Optional - Not supported in edit yet)' : 'Upload Photo'}</label>
                            {!editingCase && <FileUploader onFileSelect={setSelectedImages} selectedFiles={selectedImages} />}
                            {editingCase && <p className="text-xs text-gray-500 italic">Image updates are not supported in this version. Delete and re-create if image change is needed.</p>}
                        </div>
                        <div className="md:col-span-2 flex justify-end">
                            <button type="button" onClick={() => setShowForm(false)} className="mr-3 px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md">Cancel</button>
                            <button type="submit" disabled={submitLoading} className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50">
                                {submitLoading ? 'Saving...' : (editingCase ? 'Update Details' : 'Submit Report')}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* View Case Details Modal */}
            {viewingCase && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl p-8 border-t-4 border-indigo-600">
                        <div className="flex justify-between items-start mb-6">
                            <h2 className="text-2xl font-bold text-slate-900 uppercase">Case Details: {viewingCase.full_name}</h2>
                            <button onClick={() => setViewingCase(null)} className="bg-slate-100 hover:bg-slate-200 text-slate-600 p-2 rounded-full transition-colors">
                                <X className="h-6 w-6" />
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                            <div>
                                <h3 className="text-sm font-bold text-slate-400 uppercase mb-2">Child Information</h3>
                                <div className="bg-slate-50 p-4 rounded-xl space-y-3">
                                    <p><span className="font-semibold text-slate-700">Age:</span> {viewingCase.age}</p>
                                    <p><span className="font-semibold text-slate-700">Gender:</span> {viewingCase.gender}</p>
                                    <p><span className="font-semibold text-slate-700">Status:</span> <span className={viewingCase.status === 'missing' ? 'text-red-600 font-bold' : 'text-green-600 font-bold'}>{viewingCase.status.toUpperCase()}</span></p>
                                    <p><span className="font-semibold text-slate-700">Last Seen:</span> {viewingCase.last_seen_location}</p>
                                    <p><span className="font-semibold text-slate-700">State:</span> {viewingCase.state || 'N/A'}</p>
                                    <p><span className="font-semibold text-slate-700">District:</span> {viewingCase.district || 'N/A'}</p>
                                </div>
                            </div>
                            <div>
                                <h3 className="text-sm font-bold text-slate-400 uppercase mb-2">Administrative Info</h3>
                                <div className="bg-slate-50 p-4 rounded-xl space-y-3">
                                    <p><span className="font-semibold text-slate-700">Officer Name:</span> {viewingCase.officer_name || 'N/A'}</p>
                                    <p><span className="font-semibold text-slate-700">Parent Contact:</span> {viewingCase.parent_contact_number || viewingCase.contact_phone || 'N/A'}</p>
                                    {viewingCase.is_resolved && (
                                        <p><span className="font-semibold text-green-600 bg-green-100 px-2 py-1 rounded">Resolved At:</span> {new Date(viewingCase.resolved_at).toLocaleString()}</p>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="mb-8">
                            <h3 className="text-sm font-bold text-slate-400 uppercase mb-2">Police Station Details</h3>
                            <div className="bg-indigo-50 border border-indigo-100 p-4 rounded-xl space-y-2">
                                <p><span className="font-semibold text-indigo-900">Station Name:</span> {viewingCase.station_name || 'N/A'}</p>
                                <p><span className="font-semibold text-indigo-900">Address:</span> {viewingCase.station_address || 'N/A'}</p>
                                <p><span className="font-semibold text-indigo-900">Contact Number:</span> {viewingCase.station_contact_number || 'N/A'}</p>
                            </div>
                        </div>

                        <div className="mb-8">
                            <h3 className="text-sm font-bold text-slate-400 uppercase mb-2">Description</h3>
                            <p className="text-slate-600 italic bg-slate-50 p-4 rounded-xl">"{viewingCase.description || 'No description provided.'}"</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Search and Filters */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 mb-8 flex flex-col md:flex-row gap-4 items-center justify-between">
                <div className="relative w-full md:w-96">
                    <input
                        type="text"
                        placeholder="Search by name..."
                        value={searchQuery}
                        onChange={(e) => { setSearchQuery(e.target.value); setPage(0); }}
                        className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-slate-400 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>

                <div className="flex bg-slate-100 p-1 rounded-lg">
                    {['All', 'Missing', 'Found'].map((status) => (
                        <button
                            key={status}
                            onClick={() => { setStatusFilter(status); setPage(0); }}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${statusFilter === status
                                ? 'bg-white text-indigo-600 shadow-sm'
                                : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            {status}
                        </button>
                    ))}
                </div>
            </div>

            {/* Stats Section */}
            {!loading && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col items-center justify-center text-center">
                        <span className="text-3xl font-bold text-indigo-600">{stats.total_cases}</span>
                        <span className="text-sm font-medium text-slate-500 uppercase tracking-wider">Total Reports</span>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col items-center justify-center text-center">
                        <span className="text-3xl font-bold text-red-500">{stats.missing_count}</span>
                        <span className="text-sm font-medium text-slate-500 uppercase tracking-wider">Missing Now</span>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col items-center justify-center text-center">
                        <span className="text-3xl font-bold text-green-500">{stats.found_count}</span>
                        <span className="text-sm font-medium text-slate-500 uppercase tracking-wider">Found & Safe</span>
                    </div>
                </div>
            )}

            {loading ? (
                <div className="flex justify-center py-20"><Loader2 className="animate-spin h-10 w-10 text-indigo-600" /></div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                    {cases.length === 0 ? (
                        <div className="col-span-full text-center py-20 bg-white rounded-xl border-2 border-dashed border-slate-200">
                            <p className="text-slate-400">No active cases found. Start by reporting a new case.</p>
                        </div>
                    ) : (
                        cases.map((c) => (
                            <div key={c.id} className="group bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-slate-100">
                                <div className="relative h-64 overflow-hidden bg-slate-100">
                                    {c.images && c.images.length > 0 ? (
                                        <img
                                            src={c.images[0].file_path.startsWith('http') ? c.images[0].file_path : `/${c.images[0].file_path.startsWith('/') ? c.images[0].file_path.slice(1) : c.images[0].file_path}`}
                                            alt={c.full_name}
                                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                                        />
                                    ) : (
                                        <div className="w-full h-full flex flex-col items-center justify-center text-slate-400">
                                            <AlertCircle className="h-12 w-12 mb-2" />
                                            <span>No Image Available</span>
                                        </div>
                                    )}
                                    <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${c.status === 'missing' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
                                        }`}>
                                        {c.status}
                                    </div>
                                    <div className="absolute bottom-0 right-0 p-2 flex gap-2 translate-y-full group-hover:translate-y-0 transition-transform bg-white/90 backdrop-blur-sm rounded-tl-lg shadow-lg">
                                        <button onClick={() => setReviewingMatchesCase(c)} className="p-2 text-emerald-600 hover:bg-emerald-50 rounded-md transition-colors" title="Review Matches">
                                            <Search className="h-4 w-4" />
                                        </button>
                                        <button onClick={() => handleView(c.id)} className="p-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors" title="View Case">
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                                        </button>
                                        <button onClick={() => handleEdit(c)} className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors" title="Edit Case">
                                            <Edit2 className="h-4 w-4" />
                                        </button>
                                        <button onClick={() => handleDelete(c.id)} className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors" title="Delete Case">
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                </div>
                                <div className="p-6">
                                    <h3 className="text-xl font-bold text-slate-900 group-hover:text-indigo-600 transition-colors uppercase">{c.full_name}</h3>
                                    <div className="mt-2 flex items-center gap-2 text-sm text-slate-500">
                                        <span>Age: {c.age}</span>
                                        <span className="text-slate-300">•</span>
                                        <span>{c.gender}</span>
                                    </div>
                                    <div className="mt-4 pt-4 border-t border-slate-50 space-y-3">
                                        <div className="flex items-start gap-2">
                                            <span className="text-xs font-bold text-slate-400 uppercase w-20">Last Seen</span>
                                            <span className="text-sm text-slate-600 line-clamp-1">{c.last_seen_location}</span>
                                        </div>
                                        <div className="flex items-start gap-2">
                                            <span className="text-xs font-bold text-slate-400 uppercase w-20">Contact</span>
                                            <span className="text-sm text-slate-600">{c.contact_phone || c.parent_contact_number || 'N/A'}</span>
                                        </div>
                                        <p className="text-sm text-slate-500 line-clamp-2 mt-2 italic leading-relaxed">
                                            "{c.description || 'No additional description provided.'}"
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            {reviewingMatchesCase && (
                <MatchReviewModal
                    caseData={reviewingMatchesCase}
                    onClose={() => setReviewingMatchesCase(null)}
                    onResolve={() => {
                        fetchCases();
                        fetchStats();
                    }}
                />
            )}
        </div>
    );
};

export default Dashboard;
