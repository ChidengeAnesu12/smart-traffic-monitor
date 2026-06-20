/**
 * Header Component
 * Full-width green top header bar with system branding.
 */

import { TrafficCone } from "lucide-react";

export default function Header() {
  return (
    <header className="bg-gov-green flex items-center justify-between px-6 py-3 border-b border-gov-green-dark w-full">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gov-gold rounded-full flex items-center justify-center">
          <TrafficCone size={22} className="text-gray-900" />
        </div>
        <div>
          <h1 className="text-white font-bold text-lg leading-tight">
            Smart Traffic Monitor
          </h1>
          <p className="text-green-100 text-xs">
            AI-Powered Road Safety & Traffic Analytics
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <span className="bg-gov-gold text-gray-900 text-xs font-bold px-3 py-1 rounded-full">
          SYSTEM ONLINE
        </span>
      </div>
    </header>
  );
}