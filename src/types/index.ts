export interface Region {
  name: string;
  type: 'text' | 'checkbox' | 'encirclement';
  coordinates: [number, number, number, number]; // [x1, y1, x2, y2]
  markers?: [number, number, number, number];
}

export interface Template {
  form_type: string;
  form_title: string;
  length: number;
  width: number;
  use_coordinates: boolean;
  regions: Region[];
}

export interface ProcessedData {
  extractedFields: Record<string, string | boolean>;
  confidence: number;
  processingTime: number;
}

export interface PreprocessingSettings {
  fiducialEnhancement: {
    enabled: boolean;
    kernelShape: 'rectangular' | 'elliptical' | 'cross';
    kernelSize: [number, number];
    iterations: number;
  };
  brightnessContrast: {
    enabled: boolean;
    alpha: number;
    beta: number;
  };
  denoising: {
    enabled: boolean;
    filterStrength: number;
    templateWindowSize: number;
    searchWindowSize: number;
  };
  contrastEnhancement: {
    enabled: boolean;
    clipLimit: number;
    tileGridSize: [number, number];
  };
}