import React, { useState } from "react";
import {
  SafeAreaView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  ScrollView,
  TextInput,
} from "react-native";
import { StatusBar } from "expo-status-bar";

type Tab = "Home" | "Wallet" | "Verify" | "Activity" | "Me";

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>("Home");
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("password123");
  const [token, setToken] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>("Ready");
  const [credentials, setCredentials] = useState<any[]>([]);
  const [requests, setRequests] = useState<any[]>([]);

  const API_BASE = "http://localhost:8000/api/v1";

  const handleLogin = async () => {
    try {
      let r = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!r.ok) {
        r = await fetch(`${API_BASE}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
      }
      const data = await r.json();
      if (data.access_token) {
        setToken(data.access_token);
        setStatusMessage("✓ Authenticated");
        loadData(data.access_token);
      } else {
        setStatusMessage(data.detail || "Authentication failed");
      }
    } catch (e: any) {
      setStatusMessage("API unavailable or network error");
    }
  };

  const loadData = async (authToken?: string) => {
    const activeToken = authToken || token;
    if (!activeToken) return;
    try {
      const [cRes, rRes] = await Promise.all([
        fetch(`${API_BASE}/credentials`, {
          headers: { Authorization: `Bearer ${activeToken}` },
        }),
        fetch(`${API_BASE}/verification/requests`, {
          headers: { Authorization: `Bearer ${activeToken}` },
        }),
      ]);
      if (cRes.ok) setCredentials(await cRes.json());
      if (rRes.ok) setRequests(await rRes.json());
    } catch {
      // Offline fallback
    }
  };

  const handleAddCredential = async () => {
    if (!token) return;
    try {
      const r = await fetch(`${API_BASE}/credentials`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          credential_type: "CLASS_XII",
          issuer_id: "org_cbse_gov_in",
          holder_name: "Rahul Sharma",
          passing_year: 2026,
        }),
      });
      if (r.ok) {
        setStatusMessage("✓ Class XII CBSE Credential Added");
        loadData();
      }
    } catch {
      setStatusMessage("Failed to add credential");
    }
  };

  const handleCreateRequest = async () => {
    if (!token) return;
    try {
      const r = await fetch(`${API_BASE}/verification/requests`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          requester_name: "National Testing Agency",
          credential_type: "CLASS_XII",
          purpose: "JEE Admission",
        }),
      });
      if (r.ok) {
        setStatusMessage("✓ Inbound Verification Request Created");
        loadData();
      }
    } catch {
      setStatusMessage("Failed to create request");
    }
  };

  const handleConsentAndVerify = async (requestId: string) => {
    if (!token) return;
    try {
      await fetch(`${API_BASE}/verification/requests/${requestId}/consent`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ decision: "GRANT" }),
      });
      const runRes = await fetch(`${API_BASE}/verification/requests/${requestId}/run`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const result = await runRes.json();
      setStatusMessage(
        result.proof_id
          ? `✓ Verified! Proof: ${result.proof_id}`
          : `Result: ${result.result}`
      );
      loadData();
    } catch {
      setStatusMessage("Verification error");
    }
  };

  const renderContent = () => {
    if (!token) {
      return (
        <View style={styles.contentCard}>
          <Text style={styles.heading}>Citizen Sign In / Register</Text>
          <Text style={styles.subtext}>Enter your credentials to manage sovereign wallet.</Text>
          <TextInput
            style={styles.input}
            value={email}
            onChangeText={setEmail}
            placeholder="Email address"
            autoCapitalize="none"
          />
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            placeholder="Password"
          />
          <TouchableOpacity style={styles.primaryButton} onPress={handleLogin}>
            <Text style={styles.primaryButtonText}>Authenticate</Text>
          </TouchableOpacity>
          <Text style={styles.statusText}>{statusMessage}</Text>
        </View>
      );
    }

    switch (activeTab) {
      case "Home":
        return (
          <View style={styles.contentCard}>
            <Text style={styles.greeting}>Good afternoon, Rahul</Text>
            <Text style={styles.subtext}>Your documents. Your verification. Your control.</Text>
            <View style={styles.actionRow}>
              <TouchableOpacity style={styles.primaryButton} onPress={handleAddCredential}>
                <Text style={styles.primaryButtonText}>+ Add CBSE Credential</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.secondaryButton} onPress={handleCreateRequest}>
                <Text style={styles.secondaryButtonText}>+ Create NTA Request</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.statusText}>{statusMessage}</Text>
          </View>
        );
      case "Wallet":
        return (
          <View style={styles.contentCard}>
            <Text style={styles.heading}>Document Wallet ({credentials.length})</Text>
            {credentials.map((c) => (
              <View key={c.id} style={styles.docCard}>
                <Text style={styles.docTitle}>{c.credential_type}</Text>
                <Text style={styles.docIssuer}>Issuer: {c.issuer_id} • Year: {c.passing_year}</Text>
                <Text style={styles.verifiedBadge}>✓ Level {c.verification_level} {c.status}</Text>
              </View>
            ))}
            {!credentials.length && (
              <Text style={styles.emptyText}>No credentials. Tap '+ Add CBSE Credential' on Home tab.</Text>
            )}
          </View>
        );
      case "Verify":
        return (
          <View style={styles.contentCard}>
            <Text style={styles.heading}>Verification Requests ({requests.length})</Text>
            {requests.map((r) => (
              <View key={r.id} style={styles.docCard}>
                <Text style={styles.docTitle}>{r.requester_name}</Text>
                <Text style={styles.docIssuer}>Purpose: {r.purpose}</Text>
                <Text style={styles.statusBadge}>Status: {r.status}</Text>
                {r.status !== "COMPLETED" && (
                  <TouchableOpacity
                    style={[styles.primaryButton, { marginTop: 8 }]}
                    onPress={() => handleConsentAndVerify(r.id)}
                  >
                    <Text style={styles.primaryButtonText}>Allow Consent ➔ Verify</Text>
                  </TouchableOpacity>
                )}
              </View>
            ))}
            {!requests.length && (
              <Text style={styles.emptyText}>No pending verification inquiries.</Text>
            )}
            <Text style={styles.statusText}>{statusMessage}</Text>
          </View>
        );
      case "Activity":
        return (
          <View style={styles.contentCard}>
            <Text style={styles.heading}>Sovereign Audit Activity</Text>
            <Text style={styles.subtext}>All authentication and verification events logged immutably.</Text>
          </View>
        );
      case "Me":
        return (
          <View style={styles.contentCard}>
            <Text style={styles.heading}>Profile & Security</Text>
            <Text style={styles.subtext}>Email: {email}</Text>
            <TouchableOpacity
              style={[styles.secondaryButton, { marginTop: 16 }]}
              onPress={() => setToken(null)}
            >
              <Text style={styles.secondaryButtonText}>Sign Out</Text>
            </TouchableOpacity>
          </View>
        );
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <View style={styles.header}>
        <Text style={styles.headerTitle}>DigiLocker X</Text>
      </View>
      <ScrollView style={styles.scrollArea}>{renderContent()}</ScrollView>
      <View style={styles.bottomNav}>
        {(["Home", "Wallet", "Verify", "Activity", "Me"] as Tab[]).map((tab) => (
          <TouchableOpacity
            key={tab}
            onPress={() => setActiveTab(tab)}
            style={[styles.navItem, activeTab === tab && styles.navItemActive]}
          >
            <Text style={[styles.navText, activeTab === tab && styles.navTextActive]}>{tab}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  header: { padding: 16, backgroundColor: "#ffffff", borderBottomWidth: 1, borderBottomColor: "#e2e8f0" },
  headerTitle: { fontSize: 20, fontWeight: "700", color: "#0f172a" },
  scrollArea: { flex: 1, padding: 16 },
  contentCard: { backgroundColor: "#ffffff", borderRadius: 12, padding: 20, borderWidth: 1, borderColor: "#e2e8f0" },
  greeting: { fontSize: 22, fontWeight: "700", color: "#0f172a" },
  heading: { fontSize: 18, fontWeight: "700", color: "#0f172a", marginBottom: 8 },
  subtext: { fontSize: 14, color: "#64748b", marginTop: 4 },
  statusText: { fontSize: 13, color: "#2563eb", marginTop: 12, fontWeight: "600" },
  emptyText: { fontSize: 13, color: "#94a3b8", fontStyle: "italic", marginTop: 8 },
  input: { borderWidth: 1, borderColor: "#cbd5e1", borderRadius: 8, padding: 10, marginTop: 12, fontSize: 14 },
  actionRow: { flexDirection: "column", gap: 10, marginTop: 20 },
  primaryButton: { backgroundColor: "#2563eb", paddingVertical: 12, borderRadius: 8, alignItems: "center" },
  primaryButtonText: { color: "#ffffff", fontWeight: "600" },
  secondaryButton: { backgroundColor: "#f1f5f9", paddingVertical: 12, borderRadius: 8, alignItems: "center", borderWidth: 1, borderColor: "#cbd5e1" },
  secondaryButtonText: { color: "#334155", fontWeight: "600" },
  docCard: { backgroundColor: "#f8fafc", padding: 16, borderRadius: 8, marginTop: 12, borderWidth: 1, borderColor: "#e2e8f0" },
  docTitle: { fontSize: 16, fontWeight: "600", color: "#0f172a" },
  docIssuer: { fontSize: 13, color: "#64748b", marginTop: 2 },
  verifiedBadge: { color: "#059669", fontWeight: "600", fontSize: 13, marginTop: 8 },
  statusBadge: { color: "#d97706", fontWeight: "600", fontSize: 13, marginTop: 4 },
  bottomNav: {
    flexDirection: "row",
    backgroundColor: "#ffffff",
    borderTopWidth: 1,
    borderTopColor: "#e2e8f0",
    paddingVertical: 12,
    paddingHorizontal: 8,
    justifyContent: "space-around",
  },
  navItem: { paddingVertical: 6, paddingHorizontal: 12, borderRadius: 6 },
  navItemActive: { backgroundColor: "#eff6ff" },
  navText: { fontSize: 12, color: "#64748b", fontWeight: "500" },
  navTextActive: { color: "#2563eb", fontWeight: "700" },
});
