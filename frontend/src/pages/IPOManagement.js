import { useEffect, useState } from "react";
import axios from "axios";
import { Plus, Pencil, Trash2, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import AddIPOSheet from "@/components/AddIPOSheet";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function IPOManagement() {
  const [ipos, setIpos] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [isAddIPOOpen, setIsAddIPOOpen] = useState(false);
  const [editingIPO, setEditingIPO] = useState(null);
  const [filterAccount, setFilterAccount] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchIPOs = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/ipos`);
      setIpos(response.data);
    } catch (error) {
      console.error("Error fetching IPOs:", error);
      toast.error("Failed to fetch IPOs");
    } finally {
      setLoading(false);
    }
  };

  const fetchAccounts = async () => {
    try {
      const response = await axios.get(`${API}/accounts`);
      setAccounts(response.data);
    } catch (error) {
      console.error("Error fetching accounts:", error);
    }
  };

  useEffect(() => {
    fetchIPOs();
    fetchAccounts();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this IPO?")) return;
    
    try {
      await axios.delete(`${API}/ipos/${id}`);
      toast.success("IPO deleted successfully");
      await fetchIPOs();
    } catch (error) {
      console.error("Error deleting IPO:", error);
      toast.error("Failed to delete IPO");
    }
  };

  const handleEdit = (ipo) => {
    setEditingIPO(ipo);
    setIsAddIPOOpen(true);
  };

  const getAccountName = (accountId) => {
    const account = accounts.find(acc => acc.id === accountId);
    return account ? account.account_name : "Unknown";
  };

  const filteredIPOs = ipos.filter(ipo => {
    const matchesAccount = filterAccount === "all" || ipo.demat_account_id === filterAccount;
    const matchesSearch = ipo.ipo_name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesAccount && matchesSearch;
  });

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 
              className="text-4xl md:text-5xl font-bold tracking-tight text-slate-950" 
              style={{ fontFamily: 'Manrope, sans-serif' }}
              data-testid="ipo-management-title"
            >
              IPO Management
            </h1>
            <p className="text-base text-slate-600 mt-2">Manage all your IPO applications</p>
          </div>
          <Button
            onClick={() => {
              setEditingIPO(null);
              setIsAddIPOOpen(true);
            }}
            data-testid="add-ipo-button-management"
            className="bg-slate-950 hover:bg-slate-800 text-white px-6 py-6 rounded-lg shadow-md transition-all"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add New IPO
          </Button>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)] border border-slate-200/60">
          <div className="flex gap-4 mb-6 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <Input
                placeholder="Search IPO name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                data-testid="search-ipo-input"
                className="border-slate-200 focus:border-slate-400"
              />
            </div>
            <Select value={filterAccount} onValueChange={setFilterAccount}>
              <SelectTrigger 
                className="w-[200px] border-slate-200"
                data-testid="filter-account-select"
              >
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter by account" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Accounts</SelectItem>
                {accounts.map((account) => (
                  <SelectItem key={account.id} value={account.id}>
                    {account.account_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-slate-200">
                  <TableHead className="font-semibold text-slate-950" style={{ fontFamily: 'Manrope, sans-serif' }}>IPO Name</TableHead>
                  <TableHead className="font-semibold text-slate-950" style={{ fontFamily: 'Manrope, sans-serif' }}>Lot Size</TableHead>
                  <TableHead className="font-semibold text-slate-950" style={{ fontFamily: 'Manrope, sans-serif' }}>Application Price</TableHead>
                  <TableHead className="font-semibold text-slate-950" style={{ fontFamily: 'Manrope, sans-serif' }}>Allotment Qty</TableHead>
                  <TableHead className="font-semibold text-slate-950" style={{ fontFamily: 'Manrope, sans-serif' }}>Listing Price</TableHead>
                  <TableHead className="font-semibold text-slate-950" style={{ fontFamily: 'Manrope, sans-serif' }}>P&L</TableHead>
                  <TableHead className="font-semibold text-slate-950" style={{ fontFamily: 'Manrope, sans-serif' }}>Account</TableHead>
                  <TableHead className="font-semibold text-slate-950" style={{ fontFamily: 'Manrope, sans-serif' }}>Listing Date</TableHead>
                  <TableHead className="font-semibold text-slate-950 text-right" style={{ fontFamily: 'Manrope, sans-serif' }}>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-slate-600">
                      Loading...
                    </TableCell>
                  </TableRow>
                ) : filteredIPOs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-slate-600">
                      No IPOs found. Add your first IPO to get started.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredIPOs.map((ipo) => (
                    <TableRow key={ipo.id} className="border-slate-200" data-testid={`ipo-row-${ipo.id}`}>
                      <TableCell className="font-medium" style={{ fontFamily: 'JetBrains Mono, monospace' }}>{ipo.ipo_name}</TableCell>
                      <TableCell style={{ fontFamily: 'JetBrains Mono, monospace' }}>{ipo.lot_size}</TableCell>
                      <TableCell style={{ fontFamily: 'JetBrains Mono, monospace' }}>₹{ipo.application_price}</TableCell>
                      <TableCell style={{ fontFamily: 'JetBrains Mono, monospace' }}>{ipo.allotment_quantity}</TableCell>
                      <TableCell style={{ fontFamily: 'JetBrains Mono, monospace' }}>₹{ipo.listing_price}</TableCell>
                      <TableCell 
                        className={ipo.profit_loss >= 0 ? "text-emerald-600 font-semibold" : "text-rose-600 font-semibold"}
                        style={{ fontFamily: 'JetBrains Mono, monospace' }}
                      >
                        ₹{ipo.profit_loss.toLocaleString('en-IN')}
                      </TableCell>
                      <TableCell className="text-slate-600">{getAccountName(ipo.demat_account_id)}</TableCell>
                      <TableCell style={{ fontFamily: 'JetBrains Mono, monospace' }}>{ipo.listing_date}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(ipo)}
                            data-testid={`edit-ipo-${ipo.id}`}
                            className="hover:bg-slate-100"
                          >
                            <Pencil className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(ipo.id)}
                            data-testid={`delete-ipo-${ipo.id}`}
                            className="hover:bg-rose-50 hover:text-rose-600"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>

      <AddIPOSheet 
        open={isAddIPOOpen} 
        onOpenChange={(open) => {
          setIsAddIPOOpen(open);
          if (!open) setEditingIPO(null);
        }}
        onSuccess={() => {
          fetchIPOs();
          setEditingIPO(null);
        }}
        editData={editingIPO}
      />
    </div>
  );
}
