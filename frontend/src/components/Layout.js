import { Outlet, Link, useLocation } from "react-router-dom";
import { LayoutDashboard, TrendingUp, Wallet } from "lucide-react";

export default function Layout() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const navItems = [
    { path: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
    { path: "/ipos", icon: TrendingUp, label: "IPO Management" },
    { path: "/accounts", icon: Wallet, label: "Demat Accounts" }
  ];

  return (
    <div className="flex min-h-screen bg-slate-50/50">
      <aside className="w-64 bg-white border-r border-slate-200/60 shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
        <div className="p-8">
          <h1 className="text-2xl font-bold text-slate-950 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            IPO Tracker
          </h1>
          <p className="text-sm text-slate-600 mt-2">Profit & Loss Manager</p>
        </div>
        <nav className="px-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  active
                    ? "bg-slate-950 text-white shadow-md"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
