import React, { useState } from 'react';
import searchService from '../services/search';
import casesService from '../services/cases';
import FileUploader from '../components/FileUploader';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

const Search = () => {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);
    const [selectedResult, setSelectedResult] = useState(null);

    const handleSearch = async () => {
        if (!selectedFiles || selectedFiles.length === 0) return;
        setLoading(true);
        setSearched(true);
        setResults([]);

        const formData = new FormData();
        // Since FileUploader manages an array, we grab the strictly 1st element.
        const fileToUpload = selectedFiles[0];
        formData.append('file', fileToUpload);

        try {
            // New strict JSON endpoint returns: [{ child_id, similarity, confidence_level }]
            const searchData = await searchService.searchFace(fileToUpload);

            if (searchData && searchData.length > 0) {
                const match = searchData[0];
                if (match.confidence_level === "no_match" || match.error) {
                    setResults([]);
                } else {
                    // We only use the data returned by the search API, no private fetches
                    setResults([match]);
                }
            } else {
                setResults([]);
            }
        } catch (error) {
            console.error("Search failed", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto px-4 py-10">
            <h1 className="text-3xl font-bold text-center mb-8 text-slate-900">Search Missing Database</h1>

            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 mb-10">
                <FileUploader
                    onFileSelect={setSelectedFiles}
                    selectedFiles={selectedFiles}
                    maxFiles={1}
                    helpText="Upload a clear photo to search for a match."
                />
                <div className="mt-6 flex justify-center">
                    <button
                        onClick={handleSearch}
                        disabled={selectedFiles.length === 0 || loading}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-md font-semibold disabled:opacity-50 flex items-center gap-2"
                    >
                        {loading && <Loader2 className="animate-spin h-5 w-5" />}
                        {loading ? 'Analyzing...' : 'Identify Child'}
                    </button>
                </div>
            </div>

            {searched && !loading && (
                <div>
                    <h2 className="text-xl font-bold mb-6 text-slate-800">Match Results {results.length > 0 && results[0].confidence_level === 'review_required' && <span className="text-sm font-normal text-amber-600 ml-2">(Pending Admin Verification)</span>}</h2>
                    {results.length === 0 ? (
                        <div className="text-center p-10 bg-gray-50 rounded-lg text-gray-500">
                            No strong matches found for this person.
                        </div>
                    ) : (
                        <div className="grid gap-6">
                            {results.map((result, index) => (
                                <div key={index} className="bg-white p-6 rounded-lg shadow-md border border-gray-100 flex items-center gap-6">
                                    <div className="w-32 h-32 bg-gray-200 rounded-lg flex-shrink-0 overflow-hidden border border-gray-100">
                                        {result.image_path ? (
                                            <img
                                                src={result.image_path.startsWith('http') ? result.image_path : `/${result.image_path.startsWith('/') ? result.image_path.slice(1) : result.image_path}`}
                                                alt={result.full_name}
                                                className="w-full h-full object-contain bg-slate-100"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-xs text-gray-400 font-medium bg-gray-50">
                                                No Image
                                            </div>
                                        )}
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h3 className="text-lg font-bold text-slate-900 leading-tight">
                                                    {result.full_name || 'Missing Child Match'}
                                                </h3>
                                                <div className="flex gap-2 mt-1">
                                                    <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md font-medium">
                                                        {result.age} yrs
                                                    </span>
                                                    <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md font-medium">
                                                        {result.gender}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <p className="text-xs text-gray-500 mt-2 italic">
                                            Last seen: {result.last_seen_location}
                                        </p>
                                        <div className="mt-3 flex items-center gap-2">
                                            <span className="text-[10px] font-bold text-slate-400 uppercase">AI Confidence:</span>
                                            <div className="flex-1 h-2 bg-gray-100 rounded-full max-w-[120px] overflow-hidden">
                                                <div
                                                    className={`h-full ${result.confidence_level === 'strong_match' ? 'bg-green-500' : 'bg-amber-500'}`}
                                                    style={{ width: `${result.similarity * 100}%` }}
                                                ></div>
                                            </div>
                                            <span className="text-[10px] text-slate-600 font-bold">{(result.similarity * 100).toFixed(1)}%</span>
                                        </div>
                                    </div>
                                    <div className="flex flex-col gap-2">
                                        <button
                                            onClick={() => setSelectedResult(result)}
                                            className="bg-indigo-50 text-indigo-600 px-4 py-2 rounded-lg font-bold text-xs hover:bg-indigo-100 transition-colors"
                                        >
                                            View Details
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
            {/* Details Modal */}
            {selectedResult && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
                        <div className="grid grid-cols-1 md:grid-cols-2 h-80 md:h-[400px] shrink-0 border-b border-slate-100">
                            {/* Left: Uploaded Image */}
                            <div className="relative bg-slate-100 border-r border-slate-200 overflow-hidden h-full">
                                <span className="absolute top-4 left-4 bg-slate-800/80 text-white px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider z-10">
                                    Your Upload
                                </span>
                                {selectedFiles && selectedFiles.length > 0 && (
                                    <img
                                        src={URL.createObjectURL(selectedFiles[0])}
                                        alt="Uploaded"
                                        className="w-full h-full object-contain"
                                    />
                                )}
                            </div>

                            {/* Right: Status Info */}
                            <div className="relative bg-slate-50 flex flex-col justify-center items-center p-8 text-center h-full">
                                <div className={`mb-4 p-4 rounded-full ${selectedResult.confidence_level === 'strong_match' ? 'text-green-600 bg-green-100' : 'text-amber-600 bg-amber-100'}`}>
                                    <CheckCircle size={48} />
                                </div>
                                <h3 className="text-2xl font-bold text-slate-800 mb-2">Match Located</h3>
                                <div className="flex gap-2 mb-4">
                                    <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${selectedResult.confidence_level === 'strong_match' ? 'bg-green-600 text-white' : 'bg-amber-600 text-white'}`}>
                                        {selectedResult.confidence_level === 'strong_match' ? 'Strong Match' : 'Potential Match'}
                                    </span>
                                    <span className="bg-indigo-600 text-white px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">
                                        Verification Required
                                    </span>
                                </div>
                                <p className="text-sm text-slate-600">A potential identity match was found in our secure database. Please coordinate with the officials listed below.</p>

                                <button
                                    onClick={() => setSelectedResult(null)}
                                    className="absolute top-4 right-4 bg-black/5 hover:bg-black/10 text-slate-600 p-2 rounded-full transition-colors z-20"
                                >
                                    <XCircle className="h-6 w-6" />
                                </button>
                            </div>
                        </div>

                        <div className="p-8">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                {/* Section 1: Child Details */}
                                <div>
                                    <div className="flex items-center gap-2 mb-4">
                                        <div className="h-6 w-1 bg-indigo-600 rounded-full"></div>
                                        <h2 className="text-lg font-bold text-slate-900 uppercase tracking-tight">Child Information</h2>
                                    </div>
                                    <div className="bg-slate-50 border border-slate-200 p-6 rounded-xl">
                                        <div className="mb-4">
                                            <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Full Name</p>
                                            <p className="text-xl font-bold text-slate-800">{selectedResult.full_name || 'N/A'}</p>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4 mb-4">
                                            <div>
                                                <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Age</p>
                                                <p className="font-bold text-slate-700">{selectedResult.age} years</p>
                                            </div>
                                            <div>
                                                <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Gender</p>
                                                <p className="font-bold text-slate-700">{selectedResult.gender}</p>
                                            </div>
                                        </div>

                                        <div>
                                            <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Last seen</p>
                                            <p className="font-semibold text-slate-700">{selectedResult.last_seen_location}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Section 2: Authority Details */}
                                <div>
                                    <div className="flex items-center gap-2 mb-4">
                                        <div className="h-6 w-1 bg-indigo-600 rounded-full"></div>
                                        <h2 className="text-lg font-bold text-slate-900 uppercase tracking-tight">Contact Authority</h2>
                                    </div>
                                    <div className="bg-slate-50 border border-slate-200 p-6 rounded-xl">
                                        <div className="mb-4">
                                            <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Police Station</p>
                                            <p className="text-xl font-bold text-indigo-700">{selectedResult.station_name || 'Details withheld'}</p>
                                        </div>

                                        <div className="mb-4">
                                            <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Address</p>
                                            <p className="font-semibold text-slate-700 text-sm leading-relaxed">{selectedResult.station_address || 'Address withheld'}</p>
                                        </div>

                                        <div>
                                            <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Contact Number</p>
                                            <p className="font-bold text-slate-700">{selectedResult.station_contact_number || 'N/A'}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-8 flex flex-col md:flex-row gap-4">
                                <a
                                    href={`tel:${selectedResult.station_contact_number}`}
                                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white text-center py-4 rounded-xl font-bold transition-all shadow-lg hover:shadow-indigo-500/30 flex items-center justify-center gap-2"
                                >
                                    Call Police Station
                                </a>
                                <button
                                    onClick={() => setSelectedResult(null)}
                                    className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 py-4 rounded-xl font-bold transition-all"
                                >
                                    Back to Results
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Search;
