import React, { useState, useEffect } from 'react';
import { X, CheckCircle, XCircle, Loader2, ChevronLeft, ChevronRight, AlertTriangle } from 'lucide-react';
import casesService from '../services/cases';

const MatchReviewModal = ({ caseData, onClose, onResolve }) => {
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [reviewingMatch, setReviewingMatch] = useState(null);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);
    const [submitLoading, setSubmitLoading] = useState(false);

    useEffect(() => {
        fetchMatches();
    }, [caseData.id]);

    const fetchMatches = async () => {
        try {
            const data = await casesService.getCaseMatches(caseData.id);
            setMatches(data);
            if (data.length > 0) {
                setReviewingMatch(data[0]);
            }
        } catch (error) {
            console.error("Failed to fetch matches");
        } finally {
            setLoading(false);
        }
    };

    const handleReview = async (status) => {
        if (!reviewingMatch) return;
        setSubmitLoading(true);
        try {
            await casesService.reviewMatch(reviewingMatch.id, status);
            if (status === 'verified') {
                onResolve();
                onClose();
            } else {
                // Remove from local list or refresh
                setMatches(matches.filter(m => m.id !== reviewingMatch.id));
                if (matches.length > 1) {
                    setReviewingMatch(matches.find(m => m.id !== reviewingMatch.id));
                } else {
                    setReviewingMatch(null);
                }
            }
        } catch (error) {
            alert("Failed to update match status");
        } finally {
            setSubmitLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                <div className="bg-white p-8 rounded-xl flex items-center gap-3">
                    <Loader2 className="animate-spin h-6 w-6 text-indigo-600" />
                    <span className="font-semibold text-slate-700">Loading matches...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center z-50 p-4 overflow-y-auto">
            <div className="bg-white rounded-2xl w-full max-w-6xl shadow-2xl overflow-hidden flex flex-col max-h-[95vh]">
                {/* Header */}
                <div className="px-8 py-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <div>
                        <h2 className="text-xl font-bold text-slate-900 leading-tight">Match Verification</h2>
                        <p className="text-sm text-slate-500 font-medium capitalize">Reviewing matches for: <span className="text-indigo-600 underline font-bold">{caseData.full_name}</span></p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-full transition-colors">
                        <X className="h-6 w-6 text-slate-400" />
                    </button>
                </div>

                {matches.length === 0 ? (
                    <div className="p-20 text-center">
                        <div className="bg-slate-100 h-20 w-20 rounded-full flex items-center justify-center mx-auto mb-6">
                            <CheckCircle className="h-10 w-10 text-slate-300" />
                        </div>
                        <h3 className="text-2xl font-bold text-slate-800 mb-2">No Pending Matches</h3>
                        <p className="text-slate-500 max-w-sm mx-auto">There are no more AI-generated matches to review for this case at the moment.</p>
                        <button onClick={onClose} className="mt-8 px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold shadow-lg hover:shadow-indigo-500/30 transition-all">
                            Done
                        </button>
                    </div>
                ) : (
                    <div className="flex-1 overflow-y-auto p-4 md:p-8">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-stretch">
                            {/* Left Col: Query Image (Uploaded by Citizen) */}
                            <div className="flex flex-col h-full bg-slate-50 rounded-3xl p-6 border-2 border-slate-100 shadow-inner">
                                <div className="flex justify-between items-center mb-4 px-2">
                                    <span className="bg-indigo-600 text-white px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest">
                                        Query Reflection
                                    </span>
                                    <div className="flex items-center gap-1.5 text-indigo-700 bg-indigo-50 px-3 py-1.5 rounded-lg border border-indigo-100">
                                        <AlertTriangle size={14} className="animate-pulse" />
                                        <span className="text-sm font-bold">{(reviewingMatch.similarity * 100).toFixed(1)}% AI Confidence</span>
                                    </div>
                                </div>
                                <div className="flex-1 bg-white rounded-2xl overflow-hidden shadow-sm border border-slate-200 min-h-[350px] relative">
                                    <img
                                        src={reviewingMatch.reporter_image_url}
                                        alt="Citizen Upload"
                                        className="w-full h-full object-contain"
                                    />
                                    <div className="absolute bottom-4 left-4 right-4 bg-black/60 backdrop-blur-sm text-white p-3 rounded-xl text-xs font-medium border border-white/20">
                                        This image was uploaded by a citizen searching the public database.
                                    </div>
                                </div>
                            </div>

                            {/* Right Col: Official Database Images */}
                            <div className="flex flex-col h-full bg-slate-900 rounded-3xl p-6 shadow-2xl">
                                <div className="flex justify-between items-center mb-4 px-2">
                                    <span className="bg-emerald-500 text-white px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest">
                                        Official Records
                                    </span>
                                    <div className="text-slate-400 text-sm font-medium">
                                        Photo {currentImageIndex + 1} of {caseData.images?.length || 0}
                                    </div>
                                </div>
                                <div className="relative flex-1 bg-slate-800 rounded-2xl overflow-hidden min-h-[350px] border border-slate-700">
                                    {caseData.images && caseData.images.length > 0 ? (
                                        <>
                                            <img
                                                src={caseData.images[currentImageIndex].file_path}
                                                alt="Official Record"
                                                className="w-full h-full object-contain opacity-90 hover:opacity-100 transition-opacity"
                                            />
                                            {caseData.images.length > 1 && (
                                                <div className="absolute inset-x-0 bottom-6 flex justify-center gap-4 z-20">
                                                    <button
                                                        onClick={() => setCurrentImageIndex((prev) => (prev > 0 ? prev - 1 : caseData.images.length - 1))}
                                                        className="p-3 bg-white/10 hover:bg-white/20 backdrop-blur-md rounded-full text-white transition-all border border-white/10"
                                                    >
                                                        <ChevronLeft size={24} />
                                                    </button>
                                                    <button
                                                        onClick={() => setCurrentImageIndex((prev) => (prev < caseData.images.length - 1 ? prev + 1 : 0))}
                                                        className="p-3 bg-white/10 hover:bg-white/20 backdrop-blur-md rounded-full text-white transition-all border border-white/10"
                                                    >
                                                        <ChevronRight size={24} />
                                                    </button>
                                                </div>
                                            )}
                                        </>
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center text-slate-500 font-bold italic">
                                            No official photos available
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Review Controls */}
                        <div className="mt-10 bg-slate-50 p-8 rounded-3xl border border-slate-100 flex flex-col md:flex-row items-center gap-8 justify-between">
                            <div className="text-center md:text-left">
                                <h4 className="text-lg font-bold text-slate-900 mb-1">Make Official Determination</h4>
                                <p className="text-slate-500 text-sm">Review the facial features above. Verifying will permanently resolve the case.</p>
                            </div>
                            <div className="flex gap-4 w-full md:w-auto">
                                <button
                                    onClick={() => handleReview('rejected')}
                                    disabled={submitLoading}
                                    className="flex-1 md:flex-none px-8 py-4 bg-white border-2 border-slate-200 text-slate-600 rounded-2xl font-bold hover:bg-slate-50 hover:border-slate-300 transition-all flex items-center justify-center gap-2"
                                >
                                    <XCircle size={20} /> Reject Match
                                </button>
                                <button
                                    onClick={() => handleReview('verified')}
                                    disabled={submitLoading}
                                    className="flex-1 md:flex-none px-10 py-4 bg-indigo-600 text-white rounded-2xl font-bold shadow-xl shadow-indigo-600/30 hover:bg-indigo-700 hover:-translate-y-0.5 transition-all flex items-center justify-center gap-2"
                                >
                                    {submitLoading ? <Loader2 className="animate-spin" /> : <CheckCircle size={20} />}
                                    {submitLoading ? 'Resolving...' : 'Verify & Resolve Case'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MatchReviewModal;
