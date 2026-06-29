"use client";

import "./globals.css";
import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 min-h-screen">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <div className="flex min-h-[calc(100vh-56px)]">
          <Sidebar
            open={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
          />
          <main className="flex-1 p-4 md:p-8 overflow-y-auto min-w-0">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}