/**
 * Header Component
 * Full-width green top header with hamburger menu for mobile.
 */

"use client";

import { TrafficCone, Menu } from "lucide-react";

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="bg-gov-green flex items-center justify-between px-4 md:px-6 py-3 border-b border-gov-green-dark w-full">
      <div className="flex items-center gap-3">
        {/* Hamburger — mobile only */}
        <button
          onClick={onMenuClick}
          className="md:hidden text-white mr-1"
          aria-label="Open menu"
        >
          <Menu size={22} />
        </button>

        <div className="w-9 h-9 bg-gov-gold rounded-full flex items-center justify-center flex-shrink-0">
          <TrafficCone size={20} className="text-gray-900" />
        </div>
        <div>
          <h1 className="text-white font-bold text-base md:text-lg leading-tight">
            Smart Traffic Monitor
          </h1>
          <p className="text-green-100 text-xs hidden sm:block">
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