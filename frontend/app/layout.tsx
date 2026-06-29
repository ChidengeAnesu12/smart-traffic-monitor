import type { Metadata } from "next";
import "./globals.css";
import AppShell from "@/components/AppShell";

export const metadata: Metadata = {
  title: "Smart Traffic Monitor — Zimbabwe",
  description: "Real-time traffic monitoring powered by YOLOv8 and DeepSORT",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 min-h-screen">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}