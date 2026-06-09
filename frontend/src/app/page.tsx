'use client';

import React, { useState } from 'react';
import NewsFeed from '@/components/NewsFeed';
import DetailPanel from '@/components/DetailPanel';
import { Activity, User, Phone, Mail } from 'lucide-react';
import { WebGLShader } from '@/components/ui/web-gl-shader';

export default function Home() {
  const [selectedInstrument, setSelectedInstrument] = useState<string | null>(null);

  return (
    <main className="relative min-h-screen bg-zinc-950 text-zinc-50 font-sans selection:bg-blue-500/30">
      <WebGLShader />

      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <header className="mb-12 text-center sm:text-left flex flex-col sm:flex-row items-center justify-between border-b border-zinc-800/50 pb-6">
          <div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 mb-2 flex items-center gap-3 justify-center sm:justify-start">
              <Activity className="w-8 h-8 text-blue-500" />
              FinSight AI
            </h1>
            <p className="text-zinc-400 text-sm sm:text-base max-w-xl">
              Yapay zeka analizleriyle finansal haberlerin arkasındaki duyarlılığı çözün, çift zaman dilimli RSI sinyalleriyle piyasadaki ucuz ve pahalı fırsatları anında yakalayın.
            </p>
          </div>
          <div className="mt-6 sm:mt-0">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
              Canlı Akış Aktif
            </div>
          </div>
        </header>

        {/* Main Content */}
        <NewsFeed onSelectInstrument={setSelectedInstrument} />

        {/* Contact & Support Section (Footer) */}
        <footer className="mt-20 border-t border-zinc-800/40 pt-10 pb-16">
          <div className="bg-zinc-900/35 backdrop-blur-md border border-zinc-800/50 rounded-2xl p-6 sm:p-8 max-w-xl mx-auto shadow-2xl relative overflow-hidden transition-all duration-300 hover:border-zinc-700/50">
            <div className="absolute top-0 right-0 w-32 h-32 rounded-full bg-blue-500/5 blur-2xl pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-32 h-32 rounded-full bg-emerald-500/5 blur-2xl pointer-events-none" />
            <h2 className="text-xl font-bold text-zinc-100 mb-6 text-center sm:text-left flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse"></span>
              İletişim & Destek
            </h2>
            <div className="flex flex-col gap-5 text-sm text-zinc-300">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-zinc-900/60 flex items-center justify-center border border-zinc-800/80 text-zinc-400">
                  <User className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-xs text-zinc-500 font-semibold tracking-wider uppercase">Kurucu & Geliştirici</p>
                  <p className="font-semibold text-zinc-100 text-base">Oğuz Kaan Ağan</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-zinc-900/60 flex items-center justify-center border border-zinc-800/80 text-zinc-400">
                  <Phone className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-xs text-zinc-500 font-semibold tracking-wider uppercase">Telefon</p>
                  <a href="tel:05364909959" className="font-semibold text-zinc-200 hover:text-blue-400 transition-colors text-base">0536 490 99 59</a>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-zinc-900/60 flex items-center justify-center border border-zinc-800/80 text-zinc-400">
                  <Mail className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-xs text-zinc-500 font-semibold tracking-wider uppercase">E-posta</p>
                  <a href="mailto:oguzkaanagan2016@gmail.com" className="font-semibold text-zinc-200 hover:text-blue-400 transition-colors text-base">oguzkaanagan2016@gmail.com</a>
                </div>
              </div>
            </div>
          </div>
        </footer>

        {/* Side Panel */}
        <DetailPanel 
          symbol={selectedInstrument} 
          onClose={() => setSelectedInstrument(null)} 
        />
      </div>
    </main>
  );
}
