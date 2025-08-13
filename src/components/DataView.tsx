import React from 'react';
import { CheckCircle, XCircle, FileText, Clock, Target } from 'lucide-react';
import { ProcessedData, Template, Region } from '../types';

interface DataViewProps {
  data: ProcessedData | null;
  template: Template | null;
  onRegionSelect: (region: Region) => void;
}

const DataView: React.FC<DataViewProps> = ({ data, template, onRegionSelect }) => {
  if (!data || !template) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <div className="text-center">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Data Available</h3>
          <p className="text-gray-500 text-sm">
            Process an image with a template to view extracted data
          </p>
        </div>
      </div>
    );
  }

  const formatValue = (value: string | boolean) => {
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    }
    return value || 'N/A';
  };

  const getValueIcon = (value: string | boolean) => {
    if (typeof value === 'boolean') {
      return value ? (
        <CheckCircle className="w-4 h-4 text-green-500" />
      ) : (
        <XCircle className="w-4 h-4 text-red-500" />
      );
    }
    return null;
  };

  return (
    <div className="h-full flex flex-col">
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-gray-900">Extracted Data</h2>
        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
          <div className="flex items-center space-x-1">
            <Target className="w-4 h-4" />
            <span>Confidence: {Math.round(data.confidence * 100)}%</span>
          </div>
          <div className="flex items-center space-x-1">
            <Clock className="w-4 h-4" />
            <span>Time: {Math.round(data.processingTime)}ms</span>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-4">
        {template.regions.map((region, index) => {
          const value = data.extractedFields[region.name];
          const hasValue = value !== undefined && value !== null && value !== '';
          
          return (
            <div
              key={index}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200 cursor-pointer"
              onClick={() => onRegionSelect(region)}
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-900 leading-tight">
                  {region.name}
                </h3>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  region.type === 'text' 
                    ? 'bg-blue-100 text-blue-800'
                    : region.type === 'checkbox'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-purple-100 text-purple-800'
                }`}>
                  {region.type}
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                {getValueIcon(value)}
                <span className={`text-sm ${
                  hasValue ? 'text-gray-900' : 'text-gray-400'
                }`}>
                  {formatValue(value)}
                </span>
              </div>
              
              <div className="mt-2 text-xs text-gray-500">
                Coordinates: [{region.coordinates.join(', ')}]
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-gray-50 border-t border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">
            {template.regions.length} regions processed
          </span>
          <button className="text-primary-600 hover:text-primary-700 font-medium">
            Export Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default DataView;