import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// ── Public Types ─────────────────────────────────────────────────────

export interface NewsItem {
  id: string;
  title: string;
  content: string;
  source: string;
  published_at: string;
  url?: string;
}

export interface AIAnalysisResult {
  sentiment: 'Positive' | 'Negative' | 'Neutral';
  affected_sectors: string[];
  affected_instruments: string[];
  impact_summary: string;
}

export interface AnalyzedNewsItem {
  news: NewsItem;
  analysis?: AIAnalysisResult;
}

export interface RSIData {
  period: string;
  rsi_value: number | null;
  status: 'Ucuz' | 'Nötr' | 'Pahalı' | 'Veri Yok';
}

export interface MarketDataResponse {
  symbol: string;
  current_price: number | null;
  ltf_rsi: RSIData;
  htf_rsi: RSIData;
}

export interface OHLCVCandle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// ── Admin Types ──────────────────────────────────────────────────────

export interface RSSSource {
  id: number;
  name: string;
  url: string;
  max_entries: number;
  is_active: number;
  created_at: string;
}

export interface ManualNews {
  id: string;
  title: string;
  content: string;
  source: string;
  published_at: string;
  url: string | null;
  is_active: number;
  created_at: string;
}

export interface DashboardStats {
  total_rss_sources: number;
  active_rss_sources: number;
  total_manual_news: number;
  active_manual_news: number;
}

export interface SiteSettings {
  site_title: string;
  site_description: string;
  max_news: string;
  [key: string]: string;
}

// ── Public API ───────────────────────────────────────────────────────

export const fetchNews = async (): Promise<AnalyzedNewsItem[]> => {
  const response = await api.get('/news');
  return response.data;
};

export const fetchMarketData = async (symbol: string): Promise<MarketDataResponse> => {
  const response = await api.get(`/market-data/${symbol}`);
  return response.data;
};

export const fetchChartData = async (symbol: string): Promise<OHLCVCandle[]> => {
  const response = await api.get(`/chart-data/${symbol}`);
  return response.data;
};

// ── Admin Auth ───────────────────────────────────────────────────────

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('admin_token') : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const adminLogin = async (password: string): Promise<string> => {
  const response = await api.post('/admin/login', { password });
  const token = response.data.token;
  localStorage.setItem('admin_token', token);
  return token;
};

export const adminLogout = async (): Promise<void> => {
  try {
    await api.post('/admin/logout', {}, { headers: getAuthHeaders() });
  } finally {
    localStorage.removeItem('admin_token');
  }
};

// ── Admin RSS Sources ────────────────────────────────────────────────

export const fetchRSSSources = async (): Promise<RSSSource[]> => {
  const response = await api.get('/admin/rss-sources', { headers: getAuthHeaders() });
  return response.data;
};

export const createRSSSource = async (data: { name: string; url: string; max_entries: number }): Promise<RSSSource> => {
  const response = await api.post('/admin/rss-sources', data, { headers: getAuthHeaders() });
  return response.data;
};

export const updateRSSSource = async (id: number, data: { name: string; url: string; max_entries: number; is_active: boolean }): Promise<RSSSource> => {
  const response = await api.put(`/admin/rss-sources/${id}`, data, { headers: getAuthHeaders() });
  return response.data;
};

export const deleteRSSSource = async (id: number): Promise<void> => {
  await api.delete(`/admin/rss-sources/${id}`, { headers: getAuthHeaders() });
};

// ── Admin Manual News ────────────────────────────────────────────────

export const fetchManualNews = async (): Promise<ManualNews[]> => {
  const response = await api.get('/admin/news', { headers: getAuthHeaders() });
  return response.data;
};

export const createManualNews = async (data: { title: string; content: string; source?: string; url?: string }): Promise<ManualNews> => {
  const response = await api.post('/admin/news', data, { headers: getAuthHeaders() });
  return response.data;
};

export const updateManualNews = async (id: string, data: { title: string; content: string; source: string; url: string; is_active: boolean }): Promise<ManualNews> => {
  const response = await api.put(`/admin/news/${id}`, data, { headers: getAuthHeaders() });
  return response.data;
};

export const deleteManualNews = async (id: string): Promise<void> => {
  await api.delete(`/admin/news/${id}`, { headers: getAuthHeaders() });
};

// ── Admin Stats & Settings ───────────────────────────────────────────

export const fetchDashboardStats = async (): Promise<DashboardStats> => {
  const response = await api.get('/admin/stats', { headers: getAuthHeaders() });
  return response.data;
};

export const fetchSiteSettings = async (): Promise<SiteSettings> => {
  const response = await api.get('/admin/settings', { headers: getAuthHeaders() });
  return response.data;
};

export const updateSiteSettings = async (data: Partial<SiteSettings>): Promise<SiteSettings> => {
  const response = await api.put('/admin/settings', data, { headers: getAuthHeaders() });
  return response.data;
};
