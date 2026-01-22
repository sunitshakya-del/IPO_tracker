import { useEffect, useState } from "react";
import axios from "axios";
import { Plus, Pencil, Trash2, Wallet } from "lucide-react";
import { Button } from "@/components/ui/button";
import AddAccountSheet from "@/components/AddAccountSheet";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function DematAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [isAddAccountOpen, setIsAddAccountOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [accountStats, setAccountStats] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const [accountsRes, statsRes] = await Promise.all([
        axios.get(`${API}/accounts`),
        axios.get(`${API}/dashboard/stats`)
      ]);
      
      setAccounts(accountsRes.data);
      
      const stats = {};
      statsRes.data.accounts_with_pl.forEach(acc => {
        stats[acc.id] = acc.total_pl;
      });
      setAccountStats(stats);
    } catch (error) {
      console.error("Error fetching accounts:", error);
      toast.error("Failed to fetch accounts");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this account?")) return;
    
    try {
      await axios.delete(`${API}/accounts/${id}`);
      toast.success("Account deleted successfully");
      await fetchAccounts();
    } catch (error) {
      console.error("Error deleting account:", error);
      toast.error("Failed to delete account");
    }
  };

  const handleEdit = (account) => {
    setEditingAccount(account);
    setIsAddAccountOpen(true);
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 
              className="text-4xl md:text-5xl font-bold tracking-tight text-slate-950" 
              style={{ fontFamily: 'Manrope, sans-serif' }}
              data-testid="demat-accounts-title"
            >
              Demat Accounts
            </h1>
            <p className="text-base text-slate-600 mt-2">Manage your {accounts.length} demat accounts</p>
          </div>
          <Button
            onClick={() => {
              setEditingAccount(null);
              setIsAddAccountOpen(true);
            }}
            data-testid="add-account-button"
            className="bg-slate-950 hover:bg-slate-800 text-white px-6 py-6 rounded-lg shadow-md transition-all"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add New Account
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-600" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            Loading...
          </div>
        ) : accounts.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center shadow-[0_2px_8px_rgba(0,0,0,0.04)] border border-slate-200/60">
            <Wallet className="w-16 h-16 mx-auto text-slate-400 mb-4" />
            <h3 className="text-xl font-semibold text-slate-950 mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
              No accounts yet
            </h3>
            <p className="text-slate-600 mb-6">Add your first demat account to start tracking IPOs</p>
            <Button
              onClick={() => setIsAddAccountOpen(true)}
              className="bg-slate-950 hover:bg-slate-800 text-white"
            >
              <Plus className="w-5 h-5 mr-2" />
              Add First Account
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {accounts.map((account) => {
              const pl = accountStats[account.id] || 0;
              return (
                <div
                  key={account.id}
                  data-testid={`account-card-${account.id}`}
                  className="bg-white rounded-xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_8px_24px_rgba(0,0,0,0.08)] transition-all duration-300 border border-slate-200/60"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 bg-slate-100 rounded-lg">
                      <Wallet className="w-6 h-6 text-slate-950" />
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(account)}
                        data-testid={`edit-account-${account.id}`}
                        className="hover:bg-slate-100"
                      >
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(account.id)}
                        data-testid={`delete-account-${account.id}`}
                        className="hover:bg-rose-50 hover:text-rose-600"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <h3 
                    className="text-xl font-semibold text-slate-950 mb-2" 
                    style={{ fontFamily: 'Manrope, sans-serif' }}
                  >
                    {account.account_name}
                  </h3>
                  <p className="text-sm text-slate-600 mb-4">{account.broker_name}</p>
                  <div className="pt-4 border-t border-slate-200">
                    <p className="text-sm text-slate-600 mb-1">Total P&L from this account</p>
                    <p 
                      className={`text-2xl font-semibold ${pl >= 0 ? "text-emerald-600" : "text-rose-600"}`}
                      style={{ fontFamily: 'JetBrains Mono, monospace' }}
                    >
                      ₹{pl.toLocaleString('en-IN')}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <AddAccountSheet 
        open={isAddAccountOpen} 
        onOpenChange={(open) => {
          setIsAddAccountOpen(open);
          if (!open) setEditingAccount(null);
        }}
        onSuccess={() => {
          fetchAccounts();
          setEditingAccount(null);
        }}
        editData={editingAccount}
      />
    </div>
  );
}
