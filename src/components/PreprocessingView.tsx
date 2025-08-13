import React, { useState } from 'react';
import { Settings, ToggleLeft, ToggleRight } from 'lucide-react';
import { PreprocessingSettings } from '../types';

const PreprocessingView: React.FC = () => {
  const [settings, setSettings] = useState<PreprocessingSettings>({
    fiducialEnhancement: {
      enabled: true,
      kernelShape: 'rectangular',
      kernelSize: [3, 3],
      iterations: 1,
    },
    brightnessContrast: {
      enabled: true,
      alpha: 1.5,
      beta: 10,
    },
    denoising: {
      enabled: true,
      filterStrength: 10,
      templateWindowSize: 7,
      searchWindowSize: 21,
    },
    contrastEnhancement: {
      enabled: false,
      clipLimit: 40,
      tileGridSize: [8, 8],
    },
  });

  const updateSetting = (category: keyof PreprocessingSettings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value,
      },
    }));
  };

  const ToggleSwitch: React.FC<{ enabled: boolean; onChange: (enabled: boolean) => void }> = ({ enabled, onChange }) => (
    <button
      onClick={() => onChange(!enabled)}
      className={`flex items-center space-x-1 px-2 py-1 rounded-md transition-colors ${
        enabled ? 'text-green-700 bg-green-50' : 'text-gray-500 bg-gray-50'
      }`}
    >
      {enabled ? <ToggleRight className="w-4 h-4" /> : <ToggleLeft className="w-4 h-4" />}
      <span className="text-xs font-medium">{enabled ? 'Enabled' : 'Disabled'}</span>
    </button>
  );

  const SectionCard: React.FC<{ 
    title: string; 
    subtitle?: string; 
    enabled: boolean; 
    onToggle: (enabled: boolean) => void;
    children: React.ReactNode;
  }> = ({ title, subtitle, enabled, onToggle, children }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <ToggleSwitch enabled={enabled} onChange={onToggle} />
      </div>
      {enabled && (
        <div className="space-y-3 pt-2 border-t border-gray-100">
          {children}
        </div>
      )}
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center space-x-2">
          <Settings className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">Preprocessing</h2>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          Configure image processing parameters
        </p>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-4">
        {/* Homography Alignment Section */}
        <div className="mb-6">
          <h3 className="text-sm font-bold text-gray-900 mb-3 uppercase tracking-wide">
            Homography Alignment
          </h3>
          
          <SectionCard
            title="Fiducial Enhancement"
            subtitle="Morphological Closing"
            enabled={settings.fiducialEnhancement.enabled}
            onToggle={(enabled) => updateSetting('fiducialEnhancement', 'enabled', enabled)}
          >
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Kernel Shape
              </label>
              <select
                value={settings.fiducialEnhancement.kernelShape}
                onChange={(e) => updateSetting('fiducialEnhancement', 'kernelShape', e.target.value)}
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="rectangular">Rectangular</option>
                <option value="elliptical">Elliptical</option>
                <option value="cross">Cross-shaped</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Kernel Size X
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={settings.fiducialEnhancement.kernelSize[0]}
                  onChange={(e) => updateSetting('fiducialEnhancement', 'kernelSize', [
                    parseInt(e.target.value),
                    settings.fiducialEnhancement.kernelSize[1]
                  ])}
                  className="w-full px-2 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Kernel Size Y
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={settings.fiducialEnhancement.kernelSize[1]}
                  onChange={(e) => updateSetting('fiducialEnhancement', 'kernelSize', [
                    settings.fiducialEnhancement.kernelSize[0],
                    parseInt(e.target.value)
                  ])}
                  className="w-full px-2 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Iterations
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={settings.fiducialEnhancement.iterations}
                onChange={(e) => updateSetting('fiducialEnhancement', 'iterations', parseInt(e.target.value))}
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </SectionCard>

          <div className="mt-4">
            <SectionCard
              title="Brightness and Contrast"
              enabled={settings.brightnessContrast.enabled}
              onToggle={(enabled) => updateSetting('brightnessContrast', 'enabled', enabled)}
            >
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Alpha (Brightness): {settings.brightnessContrast.alpha}
                </label>
                <input
                  type="range"
                  min="1"
                  max="3"
                  step="0.1"
                  value={settings.brightnessContrast.alpha}
                  onChange={(e) => updateSetting('brightnessContrast', 'alpha', parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Beta (Contrast): {settings.brightnessContrast.beta}
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  value={settings.brightnessContrast.beta}
                  onChange={(e) => updateSetting('brightnessContrast', 'beta', parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
            </SectionCard>
          </div>
        </div>

        {/* Data Extraction Section */}
        <div>
          <h3 className="text-sm font-bold text-gray-900 mb-3 uppercase tracking-wide">
            Data Extraction
          </h3>
          
          <SectionCard
            title="Image Denoising"
            subtitle="Fast Non-Local Means Denoising"
            enabled={settings.denoising.enabled}
            onToggle={(enabled) => updateSetting('denoising', 'enabled', enabled)}
          >
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Filter Strength: {settings.denoising.filterStrength}
              </label>
              <input
                type="range"
                min="0.01"
                max="100"
                step="0.01"
                value={settings.denoising.filterStrength}
                onChange={(e) => updateSetting('denoising', 'filterStrength', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Template Window Size
              </label>
              <input
                type="number"
                min="1"
                max="99"
                step="2"
                value={settings.denoising.templateWindowSize}
                onChange={(e) => updateSetting('denoising', 'templateWindowSize', parseInt(e.target.value))}
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Search Window Size
              </label>
              <input
                type="number"
                min="1"
                max="99"
                step="2"
                value={settings.denoising.searchWindowSize}
                onChange={(e) => updateSetting('denoising', 'searchWindowSize', parseInt(e.target.value))}
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </SectionCard>

          <div className="mt-4">
            <SectionCard
              title="Contrast Enhancement"
              subtitle="Contrast Limited Adaptive Histogram Equalization"
              enabled={settings.contrastEnhancement.enabled}
              onToggle={(enabled) => updateSetting('contrastEnhancement', 'enabled', enabled)}
            >
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Clip Limit: {settings.contrastEnhancement.clipLimit}
                </label>
                <input
                  type="range"
                  min="0.01"
                  max="100"
                  step="0.01"
                  value={settings.contrastEnhancement.clipLimit}
                  onChange={(e) => updateSetting('contrastEnhancement', 'clipLimit', parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Tile Grid X
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={settings.contrastEnhancement.tileGridSize[0]}
                    onChange={(e) => updateSetting('contrastEnhancement', 'tileGridSize', [
                      parseInt(e.target.value),
                      settings.contrastEnhancement.tileGridSize[1]
                    ])}
                    className="w-full px-2 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Tile Grid Y
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={settings.contrastEnhancement.tileGridSize[1]}
                    onChange={(e) => updateSetting('contrastEnhancement', 'tileGridSize', [
                      settings.contrastEnhancement.tileGridSize[0],
                      parseInt(e.target.value)
                    ])}
                    className="w-full px-2 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>
            </SectionCard>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PreprocessingView;