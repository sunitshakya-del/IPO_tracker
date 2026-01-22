import { useState, useEffect } from "react";
import axios from "axios";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AddAccountSheet({ open, onOpenChange, onSuccess, editData }) {
  const [formData, setFormData] = useState({
    account_name: "",
    broker_name: ""
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      if (editData) {
        setFormData({
          account_name: editData.account_name || "",
          broker_name: editData.broker_name || ""
        });
      } else {
        setFormData({
          account_name: "",
          broker_name: ""
        });
      }
    }
  }, [open, editData]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.account_name || !formData.broker_name) {
      toast.error("Please fill all fields");
      return;
    }

    setLoading(true);
    try {
      if (editData) {
        await axios.put(`${API}/accounts/${editData.id}`, formData);
        toast.success("Account updated successfully");
      } else {
        await axios.post(`${API}/accounts`, formData);
        toast.success("Account added successfully");
      }
      
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      console.error("Error saving account:", error);
      toast.error(editData ? "Failed to update account" : "Failed to add account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="sm:max-w-[500px]">
        <SheetHeader>
          <SheetTitle className="text-2xl" style={{ fontFamily: 'Manrope, sans-serif' }}>
            {editData ? "Edit Account" : "Add New Account"}
          </SheetTitle>
          <SheetDescription>
            {editData ? "Update demat account details" : "Add a new demat account to track IPOs"}
          </SheetDescription>
        </SheetHeader>
        <form onSubmit={handleSubmit} className="space-y-6 mt-6">
          <div className="space-y-2">
            <Label htmlFor="account_name">Account Name *</Label>
            <Input
              id="account_name"
              data-testid="account-name-input"
              value={formData.account_name}
              onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
              placeholder="e.g., Primary Account, Account 1"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="broker_name">Broker Name *</Label>
            <Input
              id="broker_name"
              data-testid="broker-name-input"
              value={formData.broker_name}
              onChange={(e) => setFormData({ ...formData, broker_name: e.target.value })}
              placeholder="e.g., Zerodha, Upstox, Angel One"
              required
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              data-testid="cancel-account-button"
              className="flex-1"
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              data-testid="submit-account-button"
              className="flex-1 bg-slate-950 hover:bg-slate-800"
              disabled={loading}
            >
              {loading ? "Saving..." : editData ? "Update Account" : "Add Account"}
            </Button>
          </div>
        </form>
      </SheetContent>
    </Sheet>
  );
}
