'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchDashboardStats, fetchRSSSources, fetchManualNews, fetchSiteSettings,
  createRSSSource, updateRSSSource, deleteRSSSource,
  createManualNews, updateManualNews, deleteManualNews,
  updateSiteSettings, adminLogout,
  RSSSource, ManualNews, SiteSettings,
} from '@/lib/api';
import {
  LayoutDashboard, Rss, Newspaper, Settings, LogOut, Plus, Trash2,
  Edit3, Check, X, Power, PowerOff, Loader2, Activity, ExternalLink,
  BarChart3, Globe, FileText, Save,
} from 'lucide-react';

type Tab = 'dashboard' | 'news' | 'rss' | 'settings';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const router = useRouter();
  const queryClient = useQueryClient();

  // Auth guard
  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (!token) {
      router.replace('/admin');
    }
  }, [router]);

  const handleLogout = async () => {
    await adminLogout();
    router.push('/admin');
  };

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'news', label: 'Haberler', icon: <Newspaper className="w-4 h-4" /> },
    { id: 'rss', label: 'RSS Kaynakları', icon: <Rss className="w-4 h-4" /> },
    { id: 'settings', label: 'Ayarlar', icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-zinc-900/50 border-r border-zinc-800 flex flex-col flex-shrink-0">
        <div className="p-6 border-b border-zinc-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-violet-500 to-blue-600 flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-sm text-zinc-100">FinSight AI</h2>
              <p className="text-xs text-zinc-500">Admin Panel</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-violet-500/15 text-violet-400 border border-violet-500/20'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-zinc-800">
          <a
            href="/"
            target="_blank"
            className="flex items-center gap-2 px-3 py-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors rounded-lg hover:bg-zinc-800/50"
          >
            <ExternalLink className="w-4 h-4" />
            Siteyi Görüntüle
          </a>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-2 mt-1 text-sm text-red-400 hover:text-red-300 transition-colors rounded-lg hover:bg-red-500/10"
          >
            <LogOut className="w-4 h-4" />
            Çıkış Yap
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-8">
          {activeTab === 'dashboard' && <DashboardTab />}
          {activeTab === 'news' && <NewsTab queryClient={queryClient} />}
          {activeTab === 'rss' && <RSSTab queryClient={queryClient} />}
          {activeTab === 'settings' && <SettingsTab queryClient={queryClient} />}
        </div>
      </main>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════
// Dashboard Tab
// ══════════════════════════════════════════════════════════════════════

function DashboardTab() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: fetchDashboardStats,
  });

  const statCards = [
    { label: 'Toplam RSS Kaynağı', value: stats?.total_rss_sources ?? 0, icon: <Rss className="w-5 h-5" />, color: 'from-blue-500 to-cyan-500' },
    { label: 'Aktif RSS Kaynağı', value: stats?.active_rss_sources ?? 0, icon: <Globe className="w-5 h-5" />, color: 'from-emerald-500 to-green-500' },
    { label: 'Manuel Haber', value: stats?.total_manual_news ?? 0, icon: <FileText className="w-5 h-5" />, color: 'from-violet-500 to-purple-500' },
    { label: 'Aktif Manuel Haber', value: stats?.active_manual_news ?? 0, icon: <BarChart3 className="w-5 h-5" />, color: 'from-amber-500 to-orange-500' },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-violet-500" />
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-8">Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => (
          <div key={card.label} className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-colors">
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${card.color} flex items-center justify-center mb-3 text-white`}>
              {card.icon}
            </div>
            <p className="text-2xl font-bold text-zinc-100">{card.value}</p>
            <p className="text-sm text-zinc-500 mt-1">{card.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════
// News Tab
// ══════════════════════════════════════════════════════════════════════

function NewsTab({ queryClient }: { queryClient: ReturnType<typeof useQueryClient> }) {
  const { data: newsList, isLoading } = useQuery({ queryKey: ['admin-news'], queryFn: fetchManualNews });
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ title: '', content: '', source: 'Admin', url: '' });

  const createMutation = useMutation({
    mutationFn: createManualNews,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['admin-news'] }); queryClient.invalidateQueries({ queryKey: ['admin-stats'] }); resetForm(); },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof updateManualNews>[1] }) => updateManualNews(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['admin-news'] }); setEditingId(null); },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteManualNews,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['admin-news'] }); queryClient.invalidateQueries({ queryKey: ['admin-stats'] }); },
  });

  const resetForm = () => { setForm({ title: '', content: '', source: 'Admin', url: '' }); setShowForm(false); };

  const handleCreate = () => {
    if (!form.title || !form.content) return;
    createMutation.mutate(form);
  };

  const startEdit = (news: ManualNews) => {
    setEditingId(news.id);
    setForm({ title: news.title, content: news.content, source: news.source, url: news.url || '' });
  };

  const handleUpdate = (news: ManualNews) => {
    updateMutation.mutate({ id: news.id, data: { ...form, is_active: !!news.is_active } });
  };

  const toggleActive = (news: ManualNews) => {
    updateMutation.mutate({
      id: news.id,
      data: { title: news.title, content: news.content, source: news.source, url: news.url || '', is_active: !news.is_active },
    });
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Manuel Haberler</h1>
        <button
          onClick={() => { setShowForm(!showForm); setEditingId(null); }}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          Yeni Haber
        </button>
      </div>

      {/* Create Form */}
      {showForm && (
        <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6 mb-6 space-y-4">
          <h3 className="font-semibold text-zinc-200">Yeni Haber Ekle</h3>
          <input
            value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Başlık"
            className="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
          />
          <textarea
            value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })}
            placeholder="İçerik"
            rows={4}
            className="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500/50 resize-none"
          />
          <div className="flex gap-3">
            <input
              value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value })}
              placeholder="Kaynak"
              className="flex-1 px-4 py-2.5 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
            />
            <input
              value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })}
              placeholder="URL (opsiyonel)"
              className="flex-1 px-4 py-2.5 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button onClick={resetForm} className="px-4 py-2 rounded-lg text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors">İptal</button>
            <button
              onClick={handleCreate}
              disabled={createMutation.isPending || !form.title || !form.content}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition-colors disabled:opacity-50"
            >
              {createMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
              Kaydet
            </button>
          </div>
        </div>
      )}

      {/* News List */}
      {isLoading ? (
        <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-violet-500" /></div>
      ) : !newsList?.length ? (
        <div className="text-center py-12 text-zinc-500 border border-dashed border-zinc-800 rounded-xl">
          Henüz manuel haber eklenmemiş.
        </div>
      ) : (
        <div className="space-y-3">
          {newsList.map((news) => (
            <div key={news.id} className={`bg-zinc-900/70 border rounded-xl p-5 transition-colors ${news.is_active ? 'border-zinc-800' : 'border-zinc-800/50 opacity-60'}`}>
              {editingId === news.id ? (
                <div className="space-y-3">
                  <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="w-full px-3 py-2 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/50" />
                  <textarea value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} rows={3} className="w-full px-3 py-2 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/50 resize-none" />
                  <div className="flex gap-2 justify-end">
                    <button onClick={() => setEditingId(null)} className="p-2 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"><X className="w-4 h-4" /></button>
                    <button onClick={() => handleUpdate(news)} className="p-2 rounded-lg text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10"><Check className="w-4 h-4" /></button>
                  </div>
                </div>
              ) : (
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-zinc-200 truncate">{news.title}</h3>
                    <p className="text-sm text-zinc-500 mt-1 line-clamp-2">{news.content}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-zinc-600">
                      <span>{news.source}</span>
                      <span>•</span>
                      <span>{new Date(news.published_at).toLocaleString('tr-TR')}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <button onClick={() => toggleActive(news)} className={`p-2 rounded-lg transition-colors ${news.is_active ? 'text-emerald-400 hover:bg-emerald-500/10' : 'text-zinc-500 hover:bg-zinc-800'}`} title={news.is_active ? 'Pasife al' : 'Aktife al'}>
                      {news.is_active ? <Power className="w-4 h-4" /> : <PowerOff className="w-4 h-4" />}
                    </button>
                    <button onClick={() => startEdit(news)} className="p-2 rounded-lg text-zinc-400 hover:text-blue-400 hover:bg-blue-500/10 transition-colors"><Edit3 className="w-4 h-4" /></button>
                    <button onClick={() => { if (confirm('Bu haberi silmek istediğinize emin misiniz?')) deleteMutation.mutate(news.id); }} className="p-2 rounded-lg text-zinc-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"><Trash2 className="w-4 h-4" /></button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════
// RSS Tab
// ══════════════════════════════════════════════════════════════════════

function RSSTab({ queryClient }: { queryClient: ReturnType<typeof useQueryClient> }) {
  const { data: sources, isLoading } = useQuery({ queryKey: ['admin-rss'], queryFn: fetchRSSSources });
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', url: '', max_entries: 10 });

  const createMutation = useMutation({
    mutationFn: createRSSSource,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['admin-rss'] }); queryClient.invalidateQueries({ queryKey: ['admin-stats'] }); setForm({ name: '', url: '', max_entries: 10 }); setShowForm(false); },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof updateRSSSource>[1] }) => updateRSSSource(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['admin-rss'] }); },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteRSSSource,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['admin-rss'] }); queryClient.invalidateQueries({ queryKey: ['admin-stats'] }); },
  });

  const toggleActive = (source: RSSSource) => {
    updateMutation.mutate({
      id: source.id,
      data: { name: source.name, url: source.url, max_entries: source.max_entries, is_active: !source.is_active },
    });
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">RSS Kaynakları</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          Yeni Kaynak
        </button>
      </div>

      {showForm && (
        <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6 mb-6 space-y-4">
          <h3 className="font-semibold text-zinc-200">Yeni RSS Kaynağı</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <input
              value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Kaynak Adı"
              className="px-4 py-2.5 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
            />
            <input
              value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })}
              placeholder="RSS URL"
              className="px-4 py-2.5 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
            />
            <input
              type="number" value={form.max_entries} onChange={(e) => setForm({ ...form, max_entries: parseInt(e.target.value) || 10 })}
              placeholder="Max Haber"
              className="px-4 py-2.5 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors">İptal</button>
            <button
              onClick={() => createMutation.mutate(form)}
              disabled={createMutation.isPending || !form.name || !form.url}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition-colors disabled:opacity-50"
            >
              {createMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
              Ekle
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-violet-500" /></div>
      ) : (
        <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800 text-zinc-500 text-left">
                <th className="px-5 py-3 font-medium">Kaynak</th>
                <th className="px-5 py-3 font-medium">URL</th>
                <th className="px-5 py-3 font-medium text-center">Max</th>
                <th className="px-5 py-3 font-medium text-center">Durum</th>
                <th className="px-5 py-3 font-medium text-right">İşlem</th>
              </tr>
            </thead>
            <tbody>
              {sources?.map((source) => (
                <tr key={source.id} className={`border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors ${!source.is_active ? 'opacity-50' : ''}`}>
                  <td className="px-5 py-3 font-medium text-zinc-200">{source.name}</td>
                  <td className="px-5 py-3 text-zinc-500 max-w-[200px] truncate">{source.url}</td>
                  <td className="px-5 py-3 text-center text-zinc-400">{source.max_entries}</td>
                  <td className="px-5 py-3 text-center">
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${source.is_active ? 'bg-emerald-500/15 text-emerald-400' : 'bg-zinc-700/50 text-zinc-500'}`}>
                      {source.is_active ? 'Aktif' : 'Pasif'}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-1 justify-end">
                      <button onClick={() => toggleActive(source)} className={`p-1.5 rounded-lg transition-colors ${source.is_active ? 'text-emerald-400 hover:bg-emerald-500/10' : 'text-zinc-500 hover:bg-zinc-800'}`}>
                        {source.is_active ? <Power className="w-4 h-4" /> : <PowerOff className="w-4 h-4" />}
                      </button>
                      <button onClick={() => { if (confirm('Bu kaynağı silmek istediğinize emin misiniz?')) deleteMutation.mutate(source.id); }} className="p-1.5 rounded-lg text-zinc-400 hover:text-red-400 hover:bg-red-500/10 transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════
// Settings Tab
// ══════════════════════════════════════════════════════════════════════

function SettingsTab({ queryClient }: { queryClient: ReturnType<typeof useQueryClient> }) {
  const { data: settings, isLoading } = useQuery({ queryKey: ['admin-settings'], queryFn: fetchSiteSettings });
  const [form, setForm] = useState<Partial<SiteSettings>>({});
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (settings) {
      setForm(settings);
    }
  }, [settings]);

  const mutation = useMutation({
    mutationFn: updateSiteSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-settings'] });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  if (isLoading) {
    return <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-violet-500" /></div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Site Ayarları</h1>

      <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6 space-y-5">
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">Site Başlığı</label>
          <input
            value={form.site_title || ''} onChange={(e) => setForm({ ...form, site_title: e.target.value })}
            className="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">Site Açıklaması</label>
          <textarea
            value={form.site_description || ''} onChange={(e) => setForm({ ...form, site_description: e.target.value })}
            rows={3}
            className="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500/50 resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">Maksimum Haber Sayısı</label>
          <input
            type="number"
            value={form.max_news || '20'} onChange={(e) => setForm({ ...form, max_news: e.target.value })}
            className="w-full max-w-[200px] px-4 py-2.5 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
          />
        </div>

        <div className="flex items-center gap-3 pt-2">
          <button
            onClick={() => mutation.mutate(form)}
            disabled={mutation.isPending}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors disabled:opacity-50"
          >
            {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Kaydet
          </button>
          {saved && (
            <span className="text-sm text-emerald-400 flex items-center gap-1 animate-in fade-in">
              <Check className="w-4 h-4" /> Kaydedildi!
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
