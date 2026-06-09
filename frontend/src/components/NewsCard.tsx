'use client';

import React from 'react';
import { AnalyzedNewsItem } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ExternalLink, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface NewsCardProps {
  item: AnalyzedNewsItem;
  onSelectInstrument: (symbol: string) => void;
}

export default function NewsCard({ item, onSelectInstrument }: NewsCardProps) {
  const { news, analysis } = item;
  
  let borderColor = 'border-zinc-800';
  let Icon = Minus;
  let iconColor = 'text-slate-400';

  if (analysis) {
    if (analysis.sentiment === 'Positive') {
      borderColor = 'border-green-500/50 shadow-[0_0_15px_rgba(34,197,94,0.1)]';
      Icon = TrendingUp;
      iconColor = 'text-green-500';
    } else if (analysis.sentiment === 'Negative') {
      borderColor = 'border-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.1)]';
      Icon = TrendingDown;
      iconColor = 'text-red-500';
    }
  }

  return (
    <Card className={`mb-4 transition-all duration-300 hover:scale-[1.01] bg-zinc-950/65 backdrop-blur-md ${borderColor}`}>
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg font-semibold leading-tight text-zinc-100">
              {news.title}
            </CardTitle>
            <CardDescription className="text-xs text-zinc-400 mt-1 flex items-center gap-2">
              <span>{news.source}</span>
              <span>•</span>
              <span>{new Date(news.published_at).toLocaleString('tr-TR')}</span>
            </CardDescription>
          </div>
          {analysis && (
            <Badge variant="outline" className={`ml-2 flex items-center gap-1 ${iconColor} border-current bg-transparent`}>
              <Icon className="w-3 h-3" />
              {analysis.sentiment}
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="text-sm text-zinc-300">
        <p className="line-clamp-3 mb-4">{news.content}</p>
        
        {analysis && (
          <div className="bg-zinc-800/50 rounded-lg p-3 mt-4 border border-zinc-700/50">
            <p className="text-xs text-zinc-400 italic mb-3">
              "{analysis.impact_summary}"
            </p>
            
            <div className="flex flex-col gap-2">
              {analysis.affected_sectors.length > 0 && (
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-medium text-zinc-500">Sektörler:</span>
                  {analysis.affected_sectors.map(sector => (
                    <Badge key={sector} variant="secondary" className="text-xs bg-zinc-800 text-zinc-300">
                      {sector}
                    </Badge>
                  ))}
                </div>
              )}
              
              {analysis.affected_instruments.length > 0 && (
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-medium text-zinc-500">Varlıklar:</span>
                  {analysis.affected_instruments.map(symbol => (
                    <Badge 
                      key={symbol} 
                      className="text-xs cursor-pointer hover:bg-blue-600 hover:text-white transition-colors bg-blue-500/20 text-blue-400 border border-blue-500/30"
                      onClick={() => onSelectInstrument(symbol)}
                    >
                      {symbol}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>

      {news.url && (
        <CardFooter className="pt-0">
          <a 
            href={news.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors"
          >
            Habere Git <ExternalLink className="w-3 h-3" />
          </a>
        </CardFooter>
      )}
    </Card>
  );
}
