import { useEffect } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { router } from "expo-router";

const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>LedgerX</Text>
      <Text style={styles.subtitle}>Accounting for Indian CAs & SMEs</Text>
      <TouchableOpacity style={styles.button} onPress={() => router.replace("/dashboard")}>
        <Text style={styles.buttonText}>Continue</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center", padding: 24, backgroundColor: "#0f172a" },
  title: { fontSize: 28, fontWeight: "700", color: "#fff", marginBottom: 8 },
  subtitle: { fontSize: 16, color: "#94a3b8", marginBottom: 48 },
  button: { backgroundColor: "#d4af37", paddingVertical: 14, paddingHorizontal: 32, borderRadius: 8 },
  buttonText: { color: "#0f172a", fontWeight: "600", fontSize: 16 },
});
