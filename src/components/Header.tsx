import React, { useRef } from 'react';
import { Upload, FileText, Play, Loader2 } from 'lucide-react';
import { Template } from '../types';

interface HeaderProps {
  onImageUpload: (imageUrl: string) => void;
  onTemplateSelect: (template: Template) => void;
  onProcessImage: () => void;
  templates: Template[];
  selectedTemplate: Template | null;
  hasImage: boolean;
  isProcessing: boolean;
}

const Header: React.FC<HeaderProps> = ({
  onImageUpload,
  onTemplateSelect,
  onProcessImage,
  templates,
  selectedTemplate,
  hasImage,
  isProcessing
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        onImageUpload(result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <FileText className="w-8 h-8 text-medical-600" />
              <h1 className="text-xl font-semibold text-gray-900">
                Medical Form Processor
              </h1>
            </div>
            <div className="h-6 w-px bg-gray-300" />
            <p className="text-sm text-gray-600">
              Automated extraction of handwritten medical forms
            </p>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={handleUploadClick}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-200"
            >
              <Upload className="w-4 h-4" />
              <span>Upload Image</span>
            </button>

            <select
              value={selectedTemplate?.form_type || ''}
              onChange={(e) => {
                const template = templates.find(t => t.form_type === e.target.value);
                if (template) onTemplateSelect(template);
              }}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 min-w-[200px]"
            >
              <option value="">Select Template</option>
              {templates.map((template) => (
                <option key={template.form_type} value={template.form_type}>
                  {template.form_title}
                </option>
              ))}
            </select>

            <button
              onClick={onProcessImage}
              disabled={!hasImage || !selectedTemplate || isProcessing}
              className="flex items-center space-x-2 px-4 py-2 bg-medical-600 text-white rounded-lg hover:bg-medical-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {isProcessing ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              <span>{isProcessing ? 'Processing...' : 'Process'}</span>
            </button>
          </div>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileUpload}
        className="hidden"
      />
    </header>
  );
};

export default Header;