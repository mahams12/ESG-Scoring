// src/hooks/useReportDownload.js
import { useState, useCallback } from 'react';
import { reportDownloadService } from '../services/reportDownloadService';

export const useReportDownload = () => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(null);
  const [lastDownload, setLastDownload] = useState(null);

  const downloadReport = useCallback(async (ticker, format = 'pdf', options = {}) => {
    setIsDownloading(true);
    setDownloadProgress({ status: 'preparing', message: 'Preparing report...' });

    try {
      // Simulate progress updates
      const progressSteps = [
        { status: 'collecting', message: 'Collecting ESG data...' },
        { status: 'analyzing', message: 'Running AI analysis...' },
        { status: 'generating', message: 'Generating report...' },
        { status: 'downloading', message: 'Starting download...' }
      ];

      for (let i = 0; i < progressSteps.length; i++) {
        setDownloadProgress(progressSteps[i]);
        await new Promise(resolve => setTimeout(resolve, 800)); // Simulate processing time
      }

      const result = await reportDownloadService.downloadESGReport(ticker, format, options);
      
      if (result.success) {
        setLastDownload({
          ticker,
          format,
          filename: result.filename,
          timestamp: new Date(),
          success: true
        });
        setDownloadProgress({ status: 'completed', message: 'Download completed!' });
        
        // Clear progress after a moment
        setTimeout(() => setDownloadProgress(null), 2000);
      } else {
        setDownloadProgress({ status: 'error', message: result.error });
        setTimeout(() => setDownloadProgress(null), 5000);
      }

      return result;
    } catch (error) {
      setDownloadProgress({ status: 'error', message: 'Download failed' });
      setTimeout(() => setDownloadProgress(null), 5000);
      return { success: false, error: error.message };
    } finally {
      setIsDownloading(false);
    }
  }, []);

  const cancelDownload = useCallback(() => {
    setIsDownloading(false);
    setDownloadProgress(null);
  }, []);

  const getPreview = useCallback(async (ticker) => {
    try {
      const result = await reportDownloadService.getReportPreview(ticker);
      return result;
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  return {
    downloadReport,
    cancelDownload,
    getPreview,
    isDownloading,
    downloadProgress,
    lastDownload,
    availableFormats: reportDownloadService.getAvailableFormats()
  };
};