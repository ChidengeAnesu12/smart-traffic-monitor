/**
 * Sidebar Component
 * Collapsible on mobile, always visible on desktop.
 */

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, BarChart3, History, Radio, X } from "lucide-react";

const navItems = [
  { href: "/", label: "Live Processing", icon: Activity },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/history", label: "Session History", icon: History },
  { href: "/live-stream", label: "Live CCTV", icon: Radio },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/50 z-20 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-full w-64 bg-[#2B2B2B] z-30 flex flex-col
          transform transition-transform duration-300 ease-in-out
          md:relative md:translate-x-0 md:z-auto
          ${open ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        {/* Mobile close button */}
        <div className="flex items-center justify-between px-6 py-4 md:hidden border-b border-gray-700">
          <span className="text-white font-semibold">Menu</span>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <nav className="flex-1 py-4">
          {navItems.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                onClick={onClose}
                className={`flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors ${
                  active
                    ? "bg-gov-gold text-gray-900 border-l-4 border-yellow-300"
                    : "text-gray-300 hover:bg-gov-gold hover:text-gray-900"
                }`}
              >
                <Icon size={18} />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="px-6 py-4 border-t border-gray-800">
          <p className="text-gray-500 text-xs">Independent Project</p>
          <p className="text-gray-600 text-xs">
            Not affiliated with the Government of Zimbabwe
          </p>
        </div>
      </aside>
    </>
  );
}