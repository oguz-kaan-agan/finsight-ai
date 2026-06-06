'use client';

import React, { useEffect, useRef, useState, memo, useCallback } from 'react';
import { createChart, ColorType, IChartApi, ISeriesApi, CandlestickData, CandlestickSeries, HistogramSeries, HistogramData } from 'lightweight-charts';
import { fetchChartData, OHLCVCandle } from '@/lib/api';

interface TradingViewWidgetProps {
  symbol: string;
}

function TradingViewWidget({ symbol }: TradingViewWidgetProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const initChart = useCallback(async () => {
    setLoading(true);
    setError(false);
    
    try {
      const data = await fetchChartData(symbol);
      
      if (!data || data.length === 0) {
        setError(true);
        setLoading(false);
        return;
      }

      if (chartContainerRef.current) {
        // Dispose old chart if exists
        if (chartRef.current) {
          chartRef.current.remove();
          chartRef.current = null;
          candleSeriesRef.current = null;
          volumeSeriesRef.current = null;
        }

        // Create new chart
        const chart = createChart(chartContainerRef.current, {
          layout: {
            background: { type: ColorType.Solid, color: '#09090b' },
            textColor: '#a1a1aa',
            fontSize: 12,
          },
          grid: {
            vertLines: { color: 'rgba(39, 39, 42, 0.5)' },
            horzLines: { color: 'rgba(39, 39, 42, 0.5)' },
          },
          timeScale: {
            borderColor: 'rgba(39, 39, 42, 0.8)',
            timeVisible: true,
            secondsVisible: false,
          },
          rightPriceScale: {
            borderColor: 'rgba(39, 39, 42, 0.8)',
            scaleMargins: {
              top: 0.1,
              bottom: 0.25, // Hacim için boşluk
            },
          },
          crosshair: {
            mode: 0,
            vertLine: {
              color: 'rgba(59, 130, 246, 0.3)',
              labelBackgroundColor: '#1e40af',
            },
            horzLine: {
              color: 'rgba(59, 130, 246, 0.3)',
              labelBackgroundColor: '#1e40af',
            },
          },
          autoSize: true,
        });

        // Candlestick serisi
        const candlestickSeries = chart.addSeries(CandlestickSeries, {
          upColor: '#22c55e',
          downColor: '#ef4444',
          borderVisible: false,
          wickUpColor: '#22c55e',
          wickDownColor: '#ef4444',
        });

        const formattedCandles: CandlestickData[] = data.map((d: OHLCVCandle) => ({
          time: d.time,
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
        }));

        candlestickSeries.setData(formattedCandles);

        // Hacim serisi
        const volumeSeries = chart.addSeries(HistogramSeries, {
          priceFormat: {
            type: 'volume',
          },
          priceScaleId: 'volume',
        });

        chart.priceScale('volume').applyOptions({
          scaleMargins: {
            top: 0.8,
            bottom: 0,
          },
        });

        const formattedVolume: HistogramData[] = data.map((d: OHLCVCandle) => ({
          time: d.time,
          value: d.volume,
          color: d.close >= d.open 
            ? 'rgba(34, 197, 94, 0.25)' 
            : 'rgba(239, 68, 68, 0.25)',
        }));

        volumeSeries.setData(formattedVolume);

        chart.timeScale().fitContent();
        
        chartRef.current = chart;
        candleSeriesRef.current = candlestickSeries;
        volumeSeriesRef.current = volumeSeries;
      }
    } catch (err) {
      console.error("Chart error:", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    initChart();

    return () => {
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [initChart, retryCount]);

  // Handle Resize
  useEffect(() => {
    const handleResize = () => {
      if (chartRef.current && chartContainerRef.current) {
        chartRef.current.applyOptions({ 
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight
        });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  return (
    <div className="relative w-full h-full min-h-[400px] flex items-center justify-center bg-[#09090b]">
      {loading && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#09090b]/80 backdrop-blur-sm">
          <div className="relative">
            <div className="w-10 h-10 border-3 border-blue-500/30 rounded-full"></div>
            <div className="w-10 h-10 border-3 border-blue-500 border-t-transparent rounded-full animate-spin absolute inset-0"></div>
          </div>
          <span className="mt-4 text-zinc-400 text-sm font-medium">
            {symbol} grafik verisi yükleniyor...
          </span>
        </div>
      )}
      
      {error && !loading && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-4 bg-[#09090b]">
          {/* Chart icon */}
          <div className="w-16 h-16 rounded-2xl bg-zinc-800/50 border border-zinc-700/50 flex items-center justify-center">
            <svg className="w-8 h-8 text-zinc-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
            </svg>
          </div>
          
          <div className="text-center">
            <p className="text-zinc-400 text-sm font-medium mb-1">
              <span className="text-zinc-200 font-semibold">{symbol}</span> için grafik verisi bulunamadı
            </p>
            <p className="text-zinc-600 text-xs max-w-xs">
              Bu sembol desteklenmiyor olabilir veya piyasa verisi sağlayıcısı geçici olarak yanıt vermiyordur.
            </p>
          </div>

          <button
            onClick={handleRetry}
            className="mt-2 px-4 py-2 rounded-lg bg-blue-600/20 border border-blue-500/30 text-blue-400 text-xs font-medium hover:bg-blue-600/30 hover:border-blue-500/50 transition-all duration-200 cursor-pointer"
          >
            Tekrar Dene
          </button>
        </div>
      )}
      
      <div 
        ref={chartContainerRef} 
        className={`w-full h-full absolute inset-0 ${loading || error ? 'opacity-0' : 'opacity-100'} transition-opacity duration-500`}
      />
    </div>
  );
}

export default memo(TradingViewWidget);
