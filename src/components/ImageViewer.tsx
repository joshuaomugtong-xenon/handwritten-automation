import React, { useState, useRef, useEffect } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, Move } from 'lucide-react';
import { Template, Region } from '../types';

interface ImageViewerProps {
  imageUrl: string | null;
  template: Template | null;
  selectedRegion: Region | null;
  onRegionSelect: (region: Region) => void;
}

const ImageViewer: React.FC<ImageViewerProps> = ({
  imageUrl,
  template,
  selectedRegion,
  onRegionSelect
}) => {
  const [zoom, setZoom] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  const handleZoomIn = () => setZoom(prev => Math.min(prev * 1.25, 5));
  const handleZoomOut = () => setZoom(prev => Math.max(prev / 1.25, 0.1));
  const handleReset = () => {
    setZoom(1);
    setPosition({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) { // Left mouse button
      setIsDragging(true);
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -1 : 1;
    if (delta > 0) {
      handleZoomIn();
    } else {
      handleZoomOut();
    }
  };

  const handleRegionClick = (region: Region, e: React.MouseEvent) => {
    e.stopPropagation();
    onRegionSelect(region);
  };

  const getRegionStyle = (region: Region) => {
    if (!imageRef.current) return {};
    
    const [x1, y1, x2, y2] = region.coordinates;
    const imageRect = imageRef.current.getBoundingClientRect();
    const containerRect = containerRef.current?.getBoundingClientRect();
    
    if (!containerRect) return {};
    
    // Calculate the actual image dimensions within the container
    const imageAspectRatio = imageRef.current.naturalWidth / imageRef.current.naturalHeight;
    const containerAspectRatio = imageRect.width / imageRect.height;
    
    let actualImageWidth, actualImageHeight;
    if (imageAspectRatio > containerAspectRatio) {
      actualImageWidth = imageRect.width;
      actualImageHeight = imageRect.width / imageAspectRatio;
    } else {
      actualImageHeight = imageRect.height;
      actualImageWidth = imageRect.height * imageAspectRatio;
    }
    
    // Calculate scale factors
    const scaleX = actualImageWidth / (template?.length || 1);
    const scaleY = actualImageHeight / (template?.width || 1);
    
    // Calculate region position and size
    const regionX = x1 * scaleX;
    const regionY = y1 * scaleY;
    const regionWidth = (x2 - x1) * scaleX;
    const regionHeight = (y2 - y1) * scaleY;
    
    // Center the image within the container
    const offsetX = (imageRect.width - actualImageWidth) / 2;
    const offsetY = (imageRect.height - actualImageHeight) / 2;
    
    return {
      position: 'absolute' as const,
      left: `${regionX + offsetX}px`,
      top: `${regionY + offsetY}px`,
      width: `${regionWidth}px`,
      height: `${regionHeight}px`,
    };
  };

  return (
    <div className="h-full flex flex-col bg-gray-100">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Photo Viewer</span>
            {imageUrl && (
              <span className="text-xs text-gray-500">
                Zoom: {Math.round(zoom * 100)}%
              </span>
            )}
          </div>
          
          {imageUrl && (
            <div className="flex items-center space-x-1">
              <button
                onClick={handleZoomOut}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                title="Zoom Out"
              >
                <ZoomOut className="w-4 h-4" />
              </button>
              <button
                onClick={handleZoomIn}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                title="Zoom In"
              >
                <ZoomIn className="w-4 h-4" />
              </button>
              <button
                onClick={handleReset}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                title="Reset View"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <div className="w-px h-6 bg-gray-300 mx-1" />
              <Move className="w-4 h-4 text-gray-400" />
              <span className="text-xs text-gray-500">Drag to pan</span>
            </div>
          )}
        </div>
      </div>

      {/* Image Container */}
      <div className="flex-1 relative overflow-hidden image-viewer">
        {imageUrl ? (
          <div
            ref={containerRef}
            className="w-full h-full relative cursor-move"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onWheel={handleWheel}
          >
            <img
              ref={imageRef}
              src={imageUrl}
              alt="Medical form"
              className="max-w-full max-h-full object-contain mx-auto"
              style={{
                transform: `scale(${zoom}) translate(${position.x / zoom}px, ${position.y / zoom}px)`,
                transformOrigin: 'center center',
                transition: isDragging ? 'none' : 'transform 0.1s ease-out',
              }}
              draggable={false}
            />
            
            {/* Region Overlays */}
            {template?.regions.map((region, index) => (
              <div
                key={index}
                className={`region-box ${selectedRegion === region ? 'selected' : ''}`}
                style={getRegionStyle(region)}
                onClick={(e) => handleRegionClick(region, e)}
                title={region.name}
              >
                <div className="absolute -top-6 left-0 bg-primary-600 text-white text-xs px-2 py-1 rounded whitespace-nowrap opacity-0 hover:opacity-100 transition-opacity">
                  {region.name}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No Image Selected
              </h3>
              <p className="text-gray-500 mb-4">
                Upload a medical form image to get started
              </p>
              <button
                onClick={handleUploadClick}
                className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-200 mx-auto"
              >
                <Upload className="w-4 h-4" />
                <span>Upload Image</span>
              </button>
            </div>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileUpload}
        className="hidden"
      />
    </div>
  );
};

export default ImageViewer;