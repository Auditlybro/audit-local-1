import { View, Text, StyleSheet, ScrollView } from "react-native";

export default function Notifications() {
  const items = [
    { type: "gst", title: "GSTR-1 due", detail: "Jan 2025 — Due 11 Feb", urgent: true },
    { type: "payment", title: "Payment reminder", detail: "ABC Traders — ₹ 25,000 overdue", urgent: true },
    { type: "stock", title: "Low stock", detail: "Item A — 5 units left", urgent: false },
    { type: "notice", title: "Notice deadline", detail: "Reply to GST notice by 20 Feb", urgent: true },
  ];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.pageTitle}>Notifications</Text>
      {items.map((item, i) => (
        <View key={i} style={[styles.card, item.urgent && styles.cardUrgent]}>
          <Text style={styles.cardTitle}>{item.title}</Text>
          <Text style={styles.cardDetail}>{item.detail}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a" },
  content: { padding: 16, paddingBottom: 32 },
  pageTitle: { fontSize: 24, fontWeight: "700", color: "#fff", marginBottom: 16 },
  card: { backgroundColor: "#1e293b", borderRadius: 12, padding: 16, marginBottom: 12 },
  cardUrgent: { borderLeftWidth: 4, borderLeftColor: "#ef4444" },
  cardTitle: { fontSize: 16, fontWeight: "600", color: "#fff" },
  cardDetail: { color: "#94a3b8", marginTop: 4 },
});
