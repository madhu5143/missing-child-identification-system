import React, { useCallback } from 'react';
import { UploadCloud, X } from 'lucide-react';

const FileUploader = ({ onFileSelect, selectedFiles, maxFiles = 5, helpText = "Please provide at least 3 distinct photos." }) => {
    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const newFiles = Array.from(e.dataTransfer.files);
            onFileSelect(prev => [...prev, ...newFiles].slice(0, maxFiles));
        }
    }, [onFileSelect, maxFiles]);

    const handleChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const newFiles = Array.from(e.target.files);
            onFileSelect(prev => [...prev, ...newFiles].slice(0, maxFiles));
        }
    };

    const removeFile = (e, index) => {
        e.stopPropagation();
        onFileSelect(prev => prev.filter((_, i) => i !== index));
    };

    return (
        <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-500 transition-colors cursor-pointer bg-gray-50 hover:bg-white relative overflow-hidden"
            onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
            onDrop={handleDrop}
            onClick={() => document.getElementById('fileInput').click()}
        >
            <input
                id="fileInput"
                type="file"
                className="hidden"
                multiple={maxFiles > 1}
                onChange={handleChange}
                accept="image/*"
            />

            {selectedFiles && selectedFiles.length > 0 ? (
                <div className="relative z-10">
                    <div className={`grid gap-4 mb-4 ${maxFiles > 1 ? 'grid-cols-2 md:grid-cols-3' : 'grid-cols-1'}`}>
                        {selectedFiles.map((file, idx) => (
                            <div key={idx} className="relative group rounded-md overflow-hidden shadow-sm border border-gray-200">
                                <img
                                    src={URL.createObjectURL(file)}
                                    alt={`Preview ${idx + 1}`}
                                    className="w-full h-64 object-contain bg-slate-100"
                                />
                                <button
                                    onClick={(e) => removeFile(e, idx)}
                                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        ))}
                    </div>
                    {selectedFiles.length < maxFiles && (
                        <div className="p-2 bg-indigo-50 rounded text-sm text-indigo-700 font-medium inline-block">
                            + Add more images ({selectedFiles.length}/{maxFiles} max)
                        </div>
                    )}
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center py-8">
                    <UploadCloud className="h-12 w-12 text-gray-400 mb-2" />
                    <p className="text-sm text-gray-600 font-medium">Click to upload or drag and drop</p>
                    <p className="text-xs text-indigo-600 font-bold mt-1">{helpText}</p>
                </div>
            )}
        </div>
    );
};

export default FileUploader;
