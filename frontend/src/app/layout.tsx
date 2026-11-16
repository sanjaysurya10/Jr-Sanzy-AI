import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import type { ReactNode } from "react";

import { BottomNav } from "@/components/layout/BottomNav";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { PLACEHOLDER_DECISIONS } from "@/lib/placeholder";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Jr Sanzy",
  description: "Jr Sanzy personal AI assistant",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full font-sans">
        <Sidebar />
        <div className="flex min-h-dvh flex-col md:pl-16 lg:pl-56">
          <Header pendingDecisionCount={PLACEHOLDER_DECISIONS.length} />
          <main className="flex-1 px-4 pb-[calc(5rem+env(safe-area-inset-bottom))] pt-4 md:pb-8 lg:px-6">
            {children}
          </main>
        </div>
        <BottomNav />
      </body>
    </html>
  );
}
