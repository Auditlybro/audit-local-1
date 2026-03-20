import { View, Text, StyleSheet, ScrollView } from "react-native";

export default function Reports() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.pageTitle}>Reports</Text>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Sales</Text>
        <Text style={styles.cardRow}>Today: ₹ 42,500</Text>
        <Text style={styles.cardRow}>This week: ₹ 2,18,000</Text>
        <Text style={styles.cardRow}>This month: ₹ 8,45,000</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Outstanding — Who owes me</Text>
        <Text style={styles.cardRow}>ABC Traders — ₹ 25,000</Text>
        <Text style={styles.cardRow}>XYZ Ltd — ₹ 18,500</Text>
        <Text style={styles.cardRow}>Retail Customer — ₹ 4,200</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Stock — What's low</Text>
        <Text style={styles.cardRow}>Item A — 5 units (reorder)</Text>
        <Text style={styles.cardRow}>Item B — 12 units</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a" },
  content: { padding: 16, paddingBottom: 32 },
  pageTitle: { fontSize: 24, fontWeight: "700", color: "#fff", marginBottom: 16 },
  card: { backgroundColor: "#1e293b", borderRadius: 12, padding: 16, marginBottom: 12 },
  cardTitle: { fontSize: 16, fontWeight: "600", color: "#d4af37", marginBottom: 12 },
  cardRow: { color: "#e2e8f0", marginBottom: 6 },
});
