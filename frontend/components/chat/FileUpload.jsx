// components/chat/FileUpload.jsx
'use client';
import React, { useState, useRef } from 'react';

const FileUpload = ({ 
  onFilesSelected, 
  acceptedTypes = ['.json', '.pdf', '.txt', '.zip', '.jpg', '.jpeg', '.png', '.gif'],
  maxSize = 10, // MB
  multiple = false,
  className = '',
  buttonText = '+',
  showPreview = true
}) => {
  const [files, setFiles] = useState([]);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);
  
  const acceptString = acceptedTypes.join(',');
  
  const handleFileChange = (e) => {
    setError('');
    const selectedFiles = Array.from(e.target.files);
    
    // Validate file types and size
    const invalidFiles = selectedFiles.filter(file => {
      const fileExtension = `.${file.name.split('.').pop().toLowerCase()}`;
      return !acceptedTypes.includes(fileExtension);
    });
    
    const oversizedFiles = selectedFiles.filter(file => 
      file.size > maxSize * 1024 * 1024
    );
    
    if (invalidFiles.length > 0) {
      setError(`Invalid file type(s): ${invalidFiles.map(f => f.name).join(', ')}`);
      return;
    }
    
    if (oversizedFiles.length > 0) {
      setError(`File(s) exceed ${maxSize}MB: ${oversizedFiles.map(f => f.name).join(', ')}`);
      return;
    }
    
    const newFiles = multiple ? [...files, ...selectedFiles] : selectedFiles;
    setFiles(newFiles);
    
    // Call the callback with selected files
    if (onFilesSelected) {
      onFilesSelected(newFiles);
    }
  };
  
  const removeFile = (index) => {
    const updatedFiles = files.filter((_, i) => i !== index);
    setFiles(updatedFiles);
    setError('');
    
    // Call the callback with updated files
    if (onFilesSelected) {
      onFilesSelected(updatedFiles);
    }
  };
  
  const getFileIcon = (file) => {
    const extension = file.name.split('.').pop().toLowerCase();
    
    // For images, return a preview
    if (['jpg', 'jpeg', 'png', 'gif'].includes(extension)) {
      return (
        <div className="w-12 h-12 overflow-hidden rounded">
          <img 
            src={URL.createObjectURL(file)} 
            alt={file.name} 
            className="w-full h-full object-cover"
          />
        </div>
      );
    }
    
    // For other file types, return an icon based on type
    const iconClasses = "w-12 h-12 flex items-center justify-center rounded";
    
    switch (extension) {
      case 'pdf':
        return (
          <div className={`${iconClasses} bg-red-100 text-red-500`}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        );
      case 'json':
        return (
          <div className={`${iconClasses} bg-yellow-100 text-yellow-500`}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        );
      case 'txt':
        return (
          <div className={`${iconClasses} bg-blue-100 text-blue-500`}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        );
      case 'zip':
        return (
          <div className={`${iconClasses} bg-purple-100 text-purple-500`}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
            </svg>
          </div>
        );
      default:
        return (
          <div className={`${iconClasses} bg-gray-100 text-gray-500`}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        );
    }
  };
  
  // Simple button version for inline use
  if (!showPreview) {
    return (
      <div className={className}>
        <button
          type="button"
          className="bg-violet-500 text-white px-4 py-2 rounded-md hover:bg-violet-600 transition-colors"
          onClick={() => fileInputRef.current.click()}
        >
          {buttonText}
        </button>
        <input
          ref={fileInputRef}
          id="file-input"
          type="file"
          multiple={multiple}
          className="hidden"
          accept={acceptString}
          onChange={handleFileChange}
        />
        {error && (
          <div className="mt-2 text-sm text-red-600">
            {error}
          </div>
        )}
      </div>
    );
  }
  
  // Full version with preview
  return (
    <div className={`w-full ${className}`}>
      <div className="border-2 border-dashed border-gray-300 rounded-md p-6">
        <div className="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <div className="mt-2">
            <p className="text-sm text-gray-500">
              Drag and drop files here, or{' '}
              <button
                type="button"
                className="text-blue-500 hover:text-blue-700 font-medium"
                onClick={() => fileInputRef.current.click()}
              >
                browse
              </button>
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Accepted formats: {acceptedTypes.join(', ')} (Max: {maxSize}MB)
            </p>
          </div>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple={multiple}
          className="hidden"
          accept={acceptString}
          onChange={handleFileChange}
        />
      </div>
      
      {error && (
        <div className="mt-2 text-sm text-red-600">
          {error}
        </div>
      )}
      
      {files.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700">Selected files:</h4>
          <ul className="mt-2 divide-y divide-gray-200">
            {files.map((file, index) => (
              <li key={index} className="py-3 flex items-center justify-between">
                <div className="flex items-center">
                  {getFileIcon(file)}
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900 truncate" style={{maxWidth: '200px'}}>
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  className="text-red-500 hover:text-red-700"
                  onClick={() => removeFile(index)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;