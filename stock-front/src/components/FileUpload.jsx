import { useCallback, useState, useRef } from 'react';
import './FileUpload.css';
import { FiUploadCloud, FiFile, FiCheck, FiX, FiLoader } from 'react-icons/fi';
import { uploadFile } from '../services/api.js';

const FileUpload = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadState, setUploadState] = useState('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const fileInputRef = useRef(null);

  const handleFile = useCallback(async (file) => {
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['xlsx', 'xls'].includes(ext)) {
      setUploadState('error');
      setStatusMessage('❌ Format non supporté. Utilisez un fichier .xlsx ou .xls');
      setTimeout(() => { setUploadState('idle'); setStatusMessage(''); }, 4000);
      return;
    }

    setUploadState('uploading');
    setStatusMessage(`Upload de ${file.name}...`);

    try {
      const result = await uploadFile(file);
      setUploadState('success');
      setStatusMessage(result.message || '✅ Fichier uploadé avec succès !');
      if (onUploadSuccess) onUploadSuccess(result);
      setTimeout(() => { setUploadState('idle'); setStatusMessage(''); }, 5000);
    } catch (error) {
      setUploadState('error');
      setStatusMessage(error.message || "❌ Erreur lors de l'upload");
      setTimeout(() => { setUploadState('idle'); setStatusMessage(''); }, 5000);
    }
  }, [onUploadSuccess]);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleInputChange = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
    e.target.value = '';
  };

  const handleClick = () => {
    if (uploadState !== 'uploading') {
      fileInputRef.current?.click();
    }
  };

  const getIcon = () => {
    switch (uploadState) {
      case 'uploading': return <FiLoader className="upload-icon spinning" />;
      case 'success': return <FiCheck className="upload-icon success" />;
      case 'error': return <FiX className="upload-icon error" />;
      default: return isDragging ? <FiFile className="upload-icon dragging" /> : <FiUploadCloud className="upload-icon" />;
    }
  };

  return (
    <div className="file-upload-container">
      <div
        id="file-upload-zone"
        className={`file-upload-zone ${isDragging ? 'dragging' : ''} ${uploadState}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        aria-label="Zone d'upload de fichier Excel"
      >
        {getIcon()}
        <div className="upload-text">
          {uploadState === 'idle' && !statusMessage && (
            <>
              <span className="upload-primary">
                {isDragging ? 'Déposez le fichier ici' : 'Cliquez ou glissez votre fichier Excel'}
              </span>
              <span className="upload-secondary">.xlsx ou .xls — Feuille « Stock actif »</span>
            </>
          )}
          {statusMessage && (
            <span className={`upload-status ${uploadState}`}>{statusMessage}</span>
          )}
        </div>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".xlsx,.xls"
        onChange={handleInputChange}
        className="file-input-hidden"
        id="excel-file-input"
        aria-hidden="true"
      />
    </div>
  );
};

export default FileUpload;
