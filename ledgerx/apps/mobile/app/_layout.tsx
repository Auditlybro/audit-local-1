import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="index" />
      <Stack.Screen name="dashboard" />
      <Stack.Screen name="new-sale" />
      <Stack.Screen name="reports" />
      <Stack.Screen name="notifications" />
    </Stack>
  );
}
