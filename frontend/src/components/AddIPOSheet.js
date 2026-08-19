import { useState, useEffect } from "react";
import api from "@/utils/api";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";

export default function AddIPOSheet({ open, onOpenChange, onSuccess, editData }) {
  const [accounts, setAccounts] = useState([]);
  const [formData, setFormData] = useState({
    ipo_name: "",
    lot_size: "",
    application_price: "",
    allotment_quantity: "",
    listing_price: "",
    sell_price: "",
    demat_account_id: "",
    application_date: "",
    listing_date: "",
    broker_charges: ""
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      fetchAccounts();
      if (editData) {
        setFormData({
          ipo_name: editData.ipo_name || "",
          lot_size: editData.lot_size?.toString() || "",
          application_price: editData.application_price?.toString() || "",
          allotment_quantity: editData.allotment_quantity?.toString() || "",
          listing_price: editData.listing_price?.toString() || "",
          sell_price: editData.sell_price?.toString() || "",
          demat_account_id: editData.demat_account_id || "",
          application_date: editData.application_date || "",
          listing_date: editData.listing_date || "",
          broker_charges: editData.broker_charges?.toString() || ""
        });
      } else {
        setFormData({
          ipo_name: "",
          lot_size: "",
          application_price: "",
          allotment_quantity: "",
          listing_price: "",
          sell_price: "",
          demat_account_id: "",
          application_date: "",
          listing_date: "",
          broker_charges: ""
        });
      }
    }
  }, [open, editData]);

  const fetchAccounts = async () => {
    try {
      const response = await api.get('/accounts');
      setAccounts(response.data);
    } catch (error) {
      console.error("Error fetching accounts:", error);
      toast.error("Failed to fetch accounts");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.ipo_name || !formData.demat_account_id) {
      toast.error("Please fill all required fields");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        ipo_name: formData.ipo_name,
        lot_size: parseInt(formData.lot_size) || 0,
        application_price: parseFloat(formData.application_price) || 0,
        allotment_quantity: parseInt(formData.allotment_quantity) || 0,
        listing_price: parseFloat(formData.listing_price) || 0,
        sell_price: parseFloat(formData.sell_price) || 0,
        demat_account_id: formData.demat_account_id,
        application_date: formData.application_date,
        listing_date: formData.listing_date,
        broker_charges: parseFloat(formData.broker_charges) || 0
      };

      if (editData) {
        await api.put(`/ipos/${editData.id}`, payload);
        toast.success("IPO updated successfully");
      } else {
        await api.post('/ipos', payload);
        toast.success("IPO added successfully");
      }
      
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      console.error("Error saving IPO:", error);
      toast.error(editData ? "Failed to update IPO" : "Failed to add IPO");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="sm:max-w-[500px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="text-2xl" style={{ fontFamily: 'Manrope, sans-serif' }}>
            {editData ? "Edit IPO" : "Add New IPO"}
          </SheetTitle>
          <SheetDescription>
            {editData ? "Update IPO details" : "Enter IPO details to track your investment"}
          </SheetDescription>
        </SheetHeader>
        <form onSubmit={handleSubmit} className="space-y-6 mt-6">
          <div className="space-y-2">
            <Label htmlFor="ipo_name">IPO Name *</Label>
            <Input
              id="ipo_name"
              data-testid="ipo-name-input"
              value={formData.ipo_name}
              onChange={(e) => setFormData({ ...formData, ipo_name: e.target.value })}
              placeholder="Enter IPO name"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="demat_account">Demat Account *</Label>
            <Select 
              value={formData.demat_account_id} 
              onValueChange={(value) => setFormData({ ...formData, demat_account_id: value })}
            >
              <SelectTrigger data-testid="demat-account-select">
                <SelectValue placeholder="Select account" />
              </SelectTrigger>
              <SelectContent>
                {accounts.map((account) => (
                  <SelectItem key={account.id} value={account.id}>
                    {account.account_name} - {account.broker_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="lot_size">Lot Size</Label>
              <Input
                id="lot_size"
                data-testid="lot-size-input"
                type="number"
                value={formData.lot_size}
                onChange={(e) => setFormData({ ...formData, lot_size: e.target.value })}
                placeholder="0"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="allotment_quantity">Allotment Qty</Label>
              <Input
                id="allotment_quantity"
                data-testid="allotment-quantity-input"
                type="number"
                value={formData.allotment_quantity}
                onChange={(e) => setFormData({ ...formData, allotment_quantity: e.target.value })}
                placeholder="0"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="application_price">Application Price (₹)</Label>
              <Input
                id="application_price"
                data-testid="application-price-input"
                type="number"
                step="0.01"
                value={formData.application_price}
                onChange={(e) => setFormData({ ...formData, application_price: e.target.value })}
                placeholder="0.00"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="listing_price">Listing Price (₹)</Label>
              <Input
                id="listing_price"
                data-testid="listing-price-input"
                type="number"
                step="0.01"
                value={formData.listing_price}
                onChange={(e) => setFormData({ ...formData, listing_price: e.target.value })}
                placeholder="0.00"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="sell_price">Sell Price (₹) *</Label>
            <Input
              id="sell_price"
              data-testid="sell-price-input"
              type="number"
              step="0.01"
              value={formData.sell_price}
              onChange={(e) => setFormData({ ...formData, sell_price: e.target.value })}
              placeholder="0.00"
              required
            />
            <p className="text-xs text-slate-500">Actual price at which you sold the IPO shares</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="broker_charges">Broker Charges (₹)</Label>
            <Input
              id="broker_charges"
              data-testid="broker-charges-input"
              type="number"
              step="0.01"
              value={formData.broker_charges}
              onChange={(e) => setFormData({ ...formData, broker_charges: e.target.value })}
              placeholder="0.00"
            />
            <p className="text-xs text-slate-500">Enter total brokerage + transaction charges</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="application_date">Application Date</Label>
              <Input
                id="application_date"
                data-testid="application-date-input"
                type="date"
                value={formData.application_date}
                onChange={(e) => setFormData({ ...formData, application_date: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="listing_date">Listing Date</Label>
              <Input
                id="listing_date"
                data-testid="listing-date-input"
                type="date"
                value={formData.listing_date}
                onChange={(e) => setFormData({ ...formData, listing_date: e.target.value })}
              />
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              data-testid="cancel-button"
              className="flex-1"
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              data-testid="submit-ipo-button"
              className="flex-1 bg-slate-950 hover:bg-slate-800"
              disabled={loading}
            >
              {loading ? "Saving..." : editData ? "Update IPO" : "Add IPO"}
            </Button>
          </div>
        </form>
      </SheetContent>
    </Sheet>
  );
}
