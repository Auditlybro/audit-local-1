import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { router } from "expo-router";

export default function NewSale() {
  const [partyName, setPartyName] = useState("");
  const [items, setItems] = useState<{ name: string; qty: string; rate: string }[]>([{ name: "", qty: "1", rate: "" }]);
  const [gstPercent] = useState(18);
  const subtotal = items.reduce((s, i) => s + (parseFloat(i.rate || "0") * parseFloat(i.qty || "0")), 0);
  const gst = (subtotal * gstPercent) / 100;
  const total = subtotal + gst;

  const addItem = () => setItems([...items, { name: "", qty: "1", rate: "" }]);
  const save = () => { /* POST to backend */ router.back(); };
  const shareWhatsApp = () => { /* Share invoice link */ };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.pageTitle}>New Sale</Text>
      <Text style={styles.label}>Party name</Text>
      <TextInput
        style={styles.input}
        placeholder="Search party..."
        placeholderTextColor="#64748b"
        value={partyName}
        onChangeText={setPartyName}
      />
      <Text style={styles.label}>Items</Text>
      {items.map((item, idx) => (
        <View key={idx} style={styles.itemRow}>
          <TextInput style={[styles.input, styles.flex]} placeholder="Stock item" placeholderTextColor="#64748b" value={item.name} onChangeText={(v) => { const n = [...items]; n[idx].name = v; setItems(n); }} />
          <TextInput style={[styles.input, styles.qty]} placeholder="Qty" placeholderTextColor="#64748b" keyboardType="numeric" value={item.qty} onChangeText={(v) => { const n = [...items]; n[idx].qty = v; setItems(n); }} />
          <TextInput style={[styles.input, styles.rate]} placeholder="Rate" placeholderTextColor="#64748b" keyboardType="numeric" value={item.rate} onChangeText={(v) => { const n = [...items]; n[idx].rate = v; setItems(n); }} />
        </View>
      ))}
      <TouchableOpacity style={styles.addBtn} onPress={addItem}>
        <Text style={styles.addBtnText}>+ Add item</Text>
      </TouchableOpacity>
      <View style={styles.summary}>
        <Text style={styles.summaryRow}>Subtotal: ₹ {subtotal.toFixed(2)}</Text>
        <Text style={styles.summaryRow}>GST ({gstPercent}%): ₹ {gst.toFixed(2)}</Text>
        <Text style={styles.totalRow}>Total: ₹ {total.toFixed(2)}</Text>
      </View>
      <TouchableOpacity style={styles.primaryBtn} onPress={save}>
        <Text style={styles.primaryBtnText}>Save</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.secondaryBtn} onPress={shareWhatsApp}>
        <Text style={styles.secondaryBtnText}>Share on WhatsApp</Text>
      </TouchableOpacity>
      <Text style={styles.razorpayNote}>Razorpay payment QR will appear on the invoice.</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a" },
  content: { padding: 16, paddingBottom: 32 },
  pageTitle: { fontSize: 24, fontWeight: "700", color: "#fff", marginBottom: 16 },
  label: { fontSize: 14, color: "#94a3b8", marginBottom: 6 },
  input: { backgroundColor: "#1e293b", borderRadius: 8, padding: 12, color: "#fff", marginBottom: 12 },
  flex: { flex: 1 },
  qty: { width: 56 },
  rate: { width: 80 },
  itemRow: { flexDirection: "row", gap: 8, marginBottom: 8 },
  addBtn: { padding: 12, marginBottom: 16 },
  addBtnText: { color: "#d4af37", fontWeight: "600" },
  summary: { backgroundColor: "#1e293b", borderRadius: 8, padding: 16, marginBottom: 16 },
  summaryRow: { color: "#94a3b8", marginBottom: 4 },
  totalRow: { fontSize: 18, fontWeight: "700", color: "#d4af37", marginTop: 8 },
  primaryBtn: { backgroundColor: "#d4af37", paddingVertical: 14, borderRadius: 8, alignItems: "center", marginBottom: 8 },
  primaryBtnText: { color: "#0f172a", fontWeight: "600" },
  secondaryBtn: { paddingVertical: 14, borderRadius: 8, alignItems: "center", borderWidth: 1, borderColor: "#d4af37", marginBottom: 8 },
  secondaryBtnText: { color: "#d4af37", fontWeight: "600" },
  razorpayNote: { fontSize: 12, color: "#64748b", textAlign: "center" },
});
