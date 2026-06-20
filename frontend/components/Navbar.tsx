/**
 * Navbar Component
 * Top navigation with Zimbabwe branding.
 */

import Link from "next/link";
import Image from "next/image";

export default function Navbar() {
  return (
    <nav className="bg-gray-900 border-b border-gray-700 px-6 py-3 flex items-center justify-between">
      {/* Logo + Title */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
          ZW
        </div>
        <div>
          <h1 className="text-white font-bold text-lg leading-tight">
            Smart Traffic Monitor
          </h1>
          <p className="text-gray-400 text-xs">Zimbabwe Road Safety System</p>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex items-center gap-6">
        <Link
          href="/"
          className="text-gray-300 hover:text-white text-sm font-medium transition-colors"
        >
          Live Processing
        </Link>
        <Link
          href="/analytics"
          className="text-gray-300 hover:text-white text-sm font-medium transition-colors"
        >
          Analytics
        </Link>
        <Link
          href="/history"
          className="text-gray-300 hover:text-white text-sm font-medium transition-colors"
        >
          Session History
        </Link>
        <span className="bg-green-600 text-white text-xs px-3 py-1 rounded-full font-medium">
          LIVE
        </span>
      </div>
    </nav>
  );
}