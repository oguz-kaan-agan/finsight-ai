'use client';

import React, { useState } from 'react';
import NewsFeed from '@/components/NewsFeed';
import DetailPanel from '@/components/DetailPanel';
import { Activity } from 'lucide-react';

export default function Home() {
  const [selectedInstrument, setSelectedInstrument] = useState<string | null>(null);

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-50 font-sans selection:bg-blue-500/30">
      {/* Background decoration */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-900/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] rounded-full bg-emerald-900/10 blur-[100px]" />
      </div>

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

        {/* Side Panel */}
        <DetailPanel 
          symbol={selectedInstrument} 
          onClose={() => setSelectedInstrument(null)} 
        />
      </div>
    </main>
  );
}
