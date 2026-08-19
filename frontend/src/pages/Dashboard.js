import { useEffect, useState } from "react";
import api from "@/utils/api";
import { Plus, TrendingUp, TrendingDown, DollarSign, Target, Award } from "lucide-react";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Button } from "@/components/ui/button";
import AddIPOSheet from "@/components/AddIPOSheet";
import { toast } from "sonner";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [isAddIPOOpen, setIsAddIPOOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching stats:", error);
      toast.error("Failed to fetch dashboard stats");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-slate-600" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
          Loading...
        </div>
      </div>
    );
  }

  const chartData = stats.recent_ipos.map((ipo) => ({
    name: ipo.ipo_name.substring(0, 10),
    pl: ipo.profit_loss
  })).reverse();

  const accountChartData = stats.accounts_with_pl.slice(0, 5).map((acc) => ({
    name: acc.account_name.substring(0, 15),
    pl: acc.total_pl
  }));

  return (
    <div className="p-4 sm:p-8">
      <div className="max-w-7xl mx-auto space-y-6 sm:space-y-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 
              className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-slate-950" 
              style={{ fontFamily: 'Manrope, sans-serif' }}
              data-testid="dashboard-title"
            >
              Dashboard
            </h1>
            <p className="text-sm sm:text-base text-slate-600 mt-2">Your IPO portfolio overview</p>
          </div>
          <Button
            onClick={() => setIsAddIPOOpen(true)}
            data-testid="add-ipo-button"
            className="bg-slate-950 hover:bg-slate-800 text-white px-4 sm:px-6 py-4 sm:py-6 rounded-lg shadow-md transition-all w-full sm:w-auto"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add New IPO
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          <div 
            className="bg-white rounded-xl p-5 sm:p-6 md:p-8 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_8px_24px_rgba(0,0,0,0.08)] transition-shadow duration-300 border border-slate-200/60"
            data-testid="total-pl-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm text-slate-600 mb-2">Total P&L</p>
                <h2 
                  className={`text-2xl sm:text-3xl font-semibold tracking-tight ${
                    stats.total_pl >= 0 ? "text-emerald-600" : "text-rose-600"
                  }`}
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  ₹{stats.total_pl.toLocaleString('en-IN')}
                </h2>
              </div>
              {stats.total_pl >= 0 ? (
                <TrendingUp className="w-8 h-8 sm:w-10 sm:h-10 text-emerald-500" />
              ) : (
                <TrendingDown className="w-8 h-8 sm:w-10 sm:h-10 text-rose-500" />
              )}
            </div>
          </div>

          <div 
            className="bg-white rounded-xl p-5 sm:p-6 md:p-8 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_8px_24px_rgba(0,0,0,0.08)] transition-shadow duration-300 border border-slate-200/60"
            data-testid="total-invested-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm text-slate-600 mb-2">Total Invested</p>
                <h2 
                  className="text-2xl sm:text-3xl font-semibold tracking-tight text-slate-950"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  ₹{stats.total_invested.toLocaleString('en-IN')}
                </h2>
              </div>
              <DollarSign className="w-8 h-8 sm:w-10 sm:h-10 text-slate-500" />
            </div>
          </div>

          <div 
            className="bg-white rounded-xl p-5 sm:p-6 md:p-8 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_8px_24px_rgba(0,0,0,0.08)] transition-shadow duration-300 border border-slate-200/60"
            data-testid="total-returns-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm text-slate-600 mb-2">Total Returns</p>
                <h2 
                  className="text-2xl sm:text-3xl font-semibold tracking-tight text-slate-950"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  ₹{stats.total_returns.toLocaleString('en-IN')}
                </h2>
              </div>
              <Target className="w-8 h-8 sm:w-10 sm:h-10 text-slate-500" />
            </div>
          </div>

          <div 
            className="bg-white rounded-xl p-5 sm:p-6 md:p-8 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_8px_24px_rgba(0,0,0,0.08)] transition-shadow duration-300 border border-slate-200/60"
            data-testid="active-ipos-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm text-slate-600 mb-2">Active IPOs</p>
                <h2 
                  className="text-2xl sm:text-3xl font-semibold tracking-tight text-slate-950"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  {stats.active_ipos}
                </h2>
              </div>
              <Award className="w-8 h-8 sm:w-10 sm:h-10 text-slate-500" />
            </div>
          </div>

          <div 
            className="bg-white rounded-xl p-5 sm:p-6 md:p-8 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_8px_24px_rgba(0,0,0,0.08)] transition-shadow duration-300 border border-slate-200/60"
            data-testid="win-rate-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm text-slate-600 mb-2">Win Rate</p>
                <h2 
                  className="text-2xl sm:text-3xl font-semibold tracking-tight text-emerald-600"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  {stats.win_rate}%
                </h2>
              </div>
              <TrendingUp className="w-8 h-8 sm:w-10 sm:h-10 text-emerald-500" />
            </div>
          </div>

          <div 
            className="col-span-1 md:col-span-2 lg:col-span-3 bg-white rounded-xl p-5 sm:p-6 md:p-8 shadow-[0_2px_8px_rgba(0,0,0,0.04)] border border-slate-200/60"
            data-testid="recent-ipos-chart"
          >
            <h3 className="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6 text-slate-950" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Recent IPO Performance
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" stroke="#64748b" style={{ fontSize: '10px', fontFamily: 'JetBrains Mono, monospace' }} />
                <YAxis stroke="#64748b" style={{ fontSize: '10px', fontFamily: 'JetBrains Mono, monospace' }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e2e8f0', 
                    borderRadius: '8px',
                    fontFamily: 'JetBrains Mono, monospace',
                    fontSize: '12px'
                  }} 
                />
                <Area type="monotone" dataKey="pl" stroke="#10b981" fill="#d1fae5" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div 
            className="col-span-1 md:col-span-2 lg:col-span-3 bg-white rounded-xl p-5 sm:p-6 md:p-8 shadow-[0_2px_8px_rgba(0,0,0,0.04)] border border-slate-200/60"
            data-testid="account-wise-pl-chart"
          >
            <h3 className="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6 text-slate-950" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Top 5 Accounts by P&L
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={accountChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" stroke="#64748b" style={{ fontSize: '10px', fontFamily: 'JetBrains Mono, monospace' }} />
                <YAxis stroke="#64748b" style={{ fontSize: '10px', fontFamily: 'JetBrains Mono, monospace' }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e2e8f0', 
                    borderRadius: '8px',
                    fontFamily: 'JetBrains Mono, monospace',
                    fontSize: '12px'
                  }} 
                />
                <Bar dataKey="pl" fill="#0f172a" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <AddIPOSheet 
        open={isAddIPOOpen} 
        onOpenChange={setIsAddIPOOpen}
        onSuccess={fetchStats}
      />
    </div>
  );
}
