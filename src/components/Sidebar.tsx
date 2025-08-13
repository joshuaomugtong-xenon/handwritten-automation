import React from 'react';
import { LucideIcon } from 'lucide-react';

interface SidebarItem {
  id: string;
  label: string;
  icon: LucideIcon;
  description: string;
}

interface SidebarProps {
  items: SidebarItem[];
  currentView: string;
  onViewChange: (view: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ items, currentView, onViewChange }) => {
  return (
    <div className="w-64 bg-white border-r border-gray-200 shadow-sm">
      <div className="p-4">
        <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-4">
          Views
        </h2>
        <nav className="space-y-2">
          {items.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className={`w-full flex items-start space-x-3 px-3 py-3 rounded-lg text-left transition-all duration-200 ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 border border-primary-200'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${
                  isActive ? 'text-primary-600' : 'text-gray-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className={`text-sm font-medium ${
                    isActive ? 'text-primary-900' : 'text-gray-900'
                  }`}>
                    {item.label}
                  </div>
                  <div className={`text-xs mt-1 ${
                    isActive ? 'text-primary-600' : 'text-gray-500'
                  }`}>
                    {item.description}
                  </div>
                </div>
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default Sidebar;