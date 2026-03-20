import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { router } from "expo-router";

// In production: fetch from API with JWT (same as web)

export default function Dashboard() {
  const todaySales = "₹ 42,500";
  const cashBalance = "₹ 15,200";
  const bankBalance = "₹ 1,28,000";
  const recent = [
    { id: "1", desc: "Sale - ABC Traders", amount: "₹ 12,000", time: "10:30" },
    { id: "2", desc: "Receipt - XYZ Ltd", amount: "₹ 8,500", time: "11:15" },
    { id: "3", desc: "Expense - Office", amount: "₹ 2,100", time: "14:00" },
    { id: "4", desc: "Sale - Retail", amount: "₹ 5,200", time: "15:45" },
    { id: "5", desc: "Payment - Supplier", amount: "₹ 18,000", time: "16:20" },
  ];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.pageTitle}>Dashboard</Text>
      <View style={styles.card}>
        <Text style={styles.cardLabel}>Today's Sales</Text>
        <Text style={styles.bigNumber}>{todaySales}</Text>
      </View>
      <View style={styles.row}>
        <View style={[styles.card, styles.halfCard]}>
          <Text style={styles.cardLabel}>Cash</Text>
          <Text style={styles.amount}>{cashBalance}</Text>
        </View>
        <View style={[styles.card, styles.halfCard]}>
          <Text style={styles.cardLabel}>Bank</Text>
          <Text style={styles.amount}>{bankBalance}</Text>
        </View>
      </View>
      <Text style={styles.sectionTitle}>Recent transactions</Text>
      {recent.map((t) => (
        <View key={t.id} style={styles.txRow}>
          <View>
            <Text style={styles.txDesc}>{t.desc}</Text>
            <Text style={styles.txTime}>{t.time}</Text>
          </View>
          <Text style={styles.txAmount}>{t.amount}</Text>
        </View>
      ))}
      <View style={styles.quickRow}>
        <TouchableOpacity style={styles.quickBtn} onPress={() => router.push("/new-sale")}>
          <Text style={styles.quickBtnText}>+ Sale</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickBtn}>
          <Text style={styles.quickBtnText}>+ Expense</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickBtn}>
          <Text style={styles.quickBtnText}>+ Receipt</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a" },
  content: { padding: 16, paddingBottom: 32 },
  pageTitle: { fontSize: 24, fontWeight: "700", color: "#fff", marginBottom: 16 },
  card: { backgroundColor: "#1e293b", borderRadius: 12, padding: 16, marginBottom: 12 },
  halfCard: { flex: 1, marginHorizontal: 4 },
  row: { flexDirection: "row", marginHorizontal: -4 },
  cardLabel: { fontSize: 12, color: "#94a3b8", marginBottom: 4 },
  bigNumber: { fontSize: 28, fontWeight: "700", color: "#d4af37" },
  amount: { fontSize: 18, fontWeight: "600", color: "#fff" },
  sectionTitle: { fontSize: 16, fontWeight: "600", color: "#fff", marginTop: 16, marginBottom: 8 },
  txRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: "#334155" },
  txDesc: { color: "#fff", fontWeight: "500" },
  txTime: { fontSize: 12, color: "#64748b", marginTop: 2 },
  txAmount: { color: "#d4af37", fontWeight: "600" },
  quickRow: { flexDirection: "row", gap: 8, marginTop: 24 },
  quickBtn: { flex: 1, backgroundColor: "#d4af37", paddingVertical: 14, borderRadius: 8, alignItems: "center" },
  quickBtnText: { color: "#0f172a", fontWeight: "600" },
});
