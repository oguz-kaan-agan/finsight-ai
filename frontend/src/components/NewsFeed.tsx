'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchNews } from '@/lib/api';
import NewsCard from './NewsCard';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface NewsFeedProps {
  onSelectInstrument: (symbol: string) => void;
}

export default function NewsFeed({ onSelectInstrument }: NewsFeedProps) {
  const { data: newsItems, isLoading, isError } = useQuery({
    queryKey: ['news'],
    queryFn: fetchNews,
    refetchInterval: 60000, // Refetch every minute
  });

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSector, setSelectedSector] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 h-48 flex flex-col justify-between">
            <Skeleton className="h-6 w-3/4 bg-zinc-800" />
            <Skeleton className="h-4 w-1/4 bg-zinc-800" />
            <Skeleton className="h-16 w-full bg-zinc-800 mt-4" />
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-center">
        Haberler yüklenirken bir hata oluştu. Lütfen bağlantınızı kontrol edin.
      </div>
    );
  }

  // Extract all unique sectors for the filter
  const allSectors = Array.from(new Set(
    newsItems?.flatMap(item => item.analysis?.affected_sectors || []) || []
  ));

  const filteredNews = newsItems?.filter(item => {
    const matchesSearch = item.news.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          item.news.content.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSector = selectedSector ? 
      item.analysis?.affected_sectors.includes(selectedSector) : true;

    return matchesSearch && matchesSector;
  });

  return (
    <div className="space-y-6">
      {/* Search and Filter Bar */}
      <div className="bg-zinc-900/80 backdrop-blur-md border border-zinc-800 p-4 rounded-xl sticky top-4 z-10 shadow-xl">
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
          <Input 
            type="text" 
            placeholder="Haberlerde ara..." 
            className="pl-9 bg-zinc-950 border-zinc-800 text-zinc-100 placeholder:text-zinc-500 focus-visible:ring-blue-500/50"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        
        {allSectors.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <Badge 
              variant="outline" 
              className={`cursor-pointer transition-colors ${selectedSector === null ? 'bg-blue-600/20 text-blue-400 border-blue-500/50' : 'bg-transparent text-zinc-400 border-zinc-700 hover:bg-zinc-800'}`}
              onClick={() => setSelectedSector(null)}
            >
              Tümü
            </Badge>
            {allSectors.map(sector => (
              <Badge 
                key={sector} 
                variant="outline" 
                className={`cursor-pointer transition-colors ${selectedSector === sector ? 'bg-blue-600/20 text-blue-400 border-blue-500/50' : 'bg-transparent text-zinc-400 border-zinc-700 hover:bg-zinc-800'}`}
                onClick={() => setSelectedSector(sector === selectedSector ? null : sector)}
              >
                {sector}
              </Badge>
            ))}
          </div>
        )}
      </div>

      {/* Feed */}
      <div className="space-y-4">
        {filteredNews?.length === 0 ? (
          <div className="text-center p-8 text-zinc-500 border border-dashed border-zinc-800 rounded-xl">
            Arama kriterlerinize uygun haber bulunamadı.
          </div>
        ) : (
          filteredNews?.map(item => (
            <NewsCard key={item.news.id} item={item} onSelectInstrument={onSelectInstrument} />
          ))
        )}
      </div>
    </div>
  );
}
