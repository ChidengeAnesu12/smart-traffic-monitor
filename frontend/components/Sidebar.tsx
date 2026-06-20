/**
 * Sidebar Component
 * Dark sidebar navigation matching government system conventions.
 */

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, BarChart3, History, Radio } from "lucide-react";

const navItems = [
  { href: "/", label: "Live Processing", icon: Activity },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/history", label: "Session History", icon: History },
  { href: "/live-stream", label: "Live CCTV", icon: Radio },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#2B2B2B] min-h-screen flex flex-col border-r border-gray-800">
      <nav className="flex-1 py-4">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
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
        <p className="text-gray-500 text-xs">
          Independent Project
        </p>
        <p className="text-gray-600 text-xs">
          Not affiliated with the Government of Zimbabwe
        </p>
      </div>
    </aside>
  );
}