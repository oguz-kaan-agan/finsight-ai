'use client';

import React from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet';
import { useQuery } from '@tanstack/react-query';
import { fetchMarketData, RSIData } from '@/lib/api';
import TradingViewWidget from './TradingViewWidget';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

interface DetailPanelProps {
  symbol: string | null;
  onClose: () => void;
}

const RsiBadge = ({ data }: { data: RSIData }) => {
  if (data.status === 'Veri Yok') {
    return <Badge variant="outline" className="text-zinc-500 border-zinc-700">Veri Yok</Badge>;
  }

  let colorClass = 'bg-slate-500/20 text-slate-400 border-slate-500/50';
  
  if (data.status === 'Ucuz') {
    colorClass = 'bg-green-500/20 text-green-400 border-green-500/50';
  } else if (data.status === 'Pahalı') {
    colorClass = 'bg-red-500/20 text-red-400 border-red-500/50';
  }

  return (
    <div className="flex flex-col items-center gap-1 bg-zinc-900/50 border border-zinc-800 p-3 rounded-xl flex-1">
      <span className="text-xs font-medium text-zinc-500 uppercase">{data.period} RSI</span>
      <div className="flex items-center gap-2">
        <span className="text-lg font-bold text-zinc-200">
          {data.rsi_value ? data.rsi_value.toFixed(2) : '-'}
        </span>
        <Badge variant="outline" className={colorClass}>
          {data.status}
        </Badge>
      </div>
    </div>
  );
};

export default function DetailPanel({ symbol, onClose }: DetailPanelProps) {
  const { data: marketData, isLoading, isError } = useQuery({
    queryKey: ['market-data', symbol],
    queryFn: () => fetchMarketData(symbol as string),
    enabled: !!symbol,
    refetchInterval: 300000, // Refetch every 5 minutes
  });

  return (
    <Sheet open={!!symbol} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full sm:max-w-xl md:max-w-2xl lg:max-w-3xl border-l-zinc-800 bg-zinc-950/95 backdrop-blur-xl p-0 flex flex-col">
        <div className="p-6 pb-0 border-b border-zinc-800/50 flex-none">
          <SheetHeader className="mb-4">
            <SheetTitle className="text-2xl font-bold text-zinc-100">{symbol}</SheetTitle>
            <SheetDescription className="text-zinc-400">
              {marketData?.current_price && (
                <span className="text-lg font-medium text-zinc-300 mr-4">
                  Son Fiyat: {marketData.current_price.toFixed(2)}
                </span>
              )}
              Teknik Analiz ve Piyasa Durumu
            </SheetDescription>
          </SheetHeader>

          {/* RSI Indicators */}
          <div className="flex gap-4 mb-6">
            {isLoading ? (
              <>
                <Skeleton className="h-20 flex-1 bg-zinc-800 rounded-xl" />
                <Skeleton className="h-20 flex-1 bg-zinc-800 rounded-xl" />
              </>
            ) : isError ? (
              <div className="w-full p-4 text-center text-red-400 bg-red-500/10 rounded-xl border border-red-500/20">
                Piyasa verisi alınamadı.
              </div>
            ) : marketData ? (
              <>
                <RsiBadge data={marketData.ltf_rsi} />
                <RsiBadge data={marketData.htf_rsi} />
              </>
            ) : null}
          </div>
        </div>

        {/* TradingView Chart */}
        <div className="flex-1 bg-black min-h-[400px]">
          {symbol && <TradingViewWidget symbol={symbol} />}
        </div>
      </SheetContent>
    </Sheet>
  );
}
