import React, { useState } from 'react';
import { FileText, Upload, Settings, Database, Eye, Edit3 } from 'lucide-react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ImageViewer from './components/ImageViewer';
import DataView from './components/DataView';
import TemplateView from './components/TemplateView';
import PreprocessingView from './components/PreprocessingView';
import { Template, ProcessedData, Region } from './types';
import { sampleTemplates } from './data/sampleTemplates';

type ViewMode = 'preprocessing' | 'data' | 'template';

function App() {
  const [currentView, setCurrentView] = useState<ViewMode>('preprocessing');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [processedData, setProcessedData] = useState<ProcessedData | null>(null);
  const [selectedRegion, setSelectedRegion] = useState<Region | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleImageUpload = (imageUrl: string) => {
    setSelectedImage(imageUrl);
    setProcessedData(null);
    setSelectedRegion(null);
  };

  const handleTemplateSelect = (template: Template) => {
    setSelectedTemplate(template);
    setProcessedData(null);
    setSelectedRegion(null);
  };

  const handleProcessImage = async () => {
    if (!selectedImage || !selectedTemplate) return;
    
    setIsProcessing(true);
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock processed data based on template
    const mockData: ProcessedData = {
      extractedFields: selectedTemplate.regions.reduce((acc, region) => {
        acc[region.name] = region.type === 'checkbox' || region.type === 'encirclement' 
          ? Math.random() > 0.5 
          : `Sample ${region.type} data`;
        return acc;
      }, {} as Record<string, string | boolean>),
      confidence: Math.random() * 0.3 + 0.7, // 70-100%
      processingTime: Math.random() * 2000 + 1000, // 1-3 seconds
    };
    
    setProcessedData(mockData);
    setIsProcessing(false);
    setCurrentView('data');
  };

  const handleRegionSelect = (region: Region) => {
    setSelectedRegion(region);
  };

  const sidebarItems = [
    {
      id: 'preprocessing' as ViewMode,
      label: 'Preprocessing',
      icon: Settings,
      description: 'Image preprocessing settings'
    },
    {
      id: 'data' as ViewMode,
      label: 'Data View',
      icon: Database,
      description: 'Extracted form data'
    },
    {
      id: 'template' as ViewMode,
      label: 'Template View',
      icon: Edit3,
      description: 'Template configuration'
    }
  ];

  const renderRightPanel = () => {
    switch (currentView) {
      case 'preprocessing':
        return <PreprocessingView />;
      case 'data':
        return (
          <DataView 
            data={processedData}
            template={selectedTemplate}
            onRegionSelect={handleRegionSelect}
          />
        );
      case 'template':
        return (
          <TemplateView 
            template={selectedTemplate}
            onRegionSelect={handleRegionSelect}
          />
        );
      default:
        return <PreprocessingView />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        onImageUpload={handleImageUpload}
        onTemplateSelect={handleTemplateSelect}
        onProcessImage={handleProcessImage}
        templates={sampleTemplates}
        selectedTemplate={selectedTemplate}
        hasImage={!!selectedImage}
        isProcessing={isProcessing}
      />
      
      <div className="flex h-[calc(100vh-4rem)]">
        <Sidebar 
          items={sidebarItems}
          currentView={currentView}
          onViewChange={setCurrentView}
        />
        
        <div className="flex-1 flex">
          <div className="flex-1 border-r border-gray-200">
            <ImageViewer 
              imageUrl={selectedImage}
              template={selectedTemplate}
              selectedRegion={selectedRegion}
              onRegionSelect={handleRegionSelect}
              onImageUpload={handleImageUpload}
            />
          </div>
          
          <div className="w-96 bg-white">
            {renderRightPanel()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;