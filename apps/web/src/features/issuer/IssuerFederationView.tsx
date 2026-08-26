import React, { useState, useEffect } from "react";
import * as api from "../../api/client";
import type {
  FederatedIssuer,
  FederatedCredential,
  RevocationRecord,
  RevocationRegistryResponse,
} from "../../types";

export const IssuerFederationView: React.FC = () => {
  const [issuers, setIssuers] = useState<FederatedIssuer[]>([]);
  const [selectedIssuerId, setSelectedIssuerId] = useState<string>("ISS-CBSE-01");
  const [credentials, setCredentials] = useState<FederatedCredential[]>([]);
  const [revocationRegistry, setRevocationRegistry] = useState<RevocationRegistryResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"credentials" | "issue" | "registry">("credentials");
  const [loading, setLoading] = useState<boolean>(true);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  // Revocation Modal State
  const [revokingCredId, setRevokingCredId] = useState<string | null>(null);
  const [revokeReason, setRevokeReason] = useState<string>("SUSPECTED_FRAUD");
  const [revokeNotes, setRevokeNotes] = useState<string>("");
  const [isSubmittingRevoke, setIsSubmittingRevoke] = useState<boolean>(false);

  // Issuance Form State
  const [issueCitizenId, setIssueCitizenId] = useState<string>("DIN-DEMO-001");
  const [issueType, setIssueType] = useState<string>("CLASS_XII_MARKSHEET");
  const [issueTitle, setIssueTitle] = useState<string>("CBSE Senior School Certificate Examination");
  const [issueStudentName, setIssueStudentName] = useState<string>("Rahul Sharma");
  const [issueRollNo, setIssueRollNo] = useState<string>("12678901");
  const [issuePercentage, setIssuePercentage] = useState<string>("88.5");
  const [issueIncomeAmount, setIssueIncomeAmount] = useState<string>("450000");
  const [issueLicenseNo, setIssueLicenseNo] = useState<string>("DL-042024009871");
  const [isSubmittingIssue, setIsSubmittingIssue] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    setActionError(null);
    try {
      const [issRes, credRes, regRes] = await Promise.all([
        api.fetchFederatedIssuers(),
        api.fetchFederatedCredentials(),
        api.fetchRevocationRegistry(),
      ]);
      setIssuers(issRes.issuers);
      setCredentials(credRes.credentials);
      setRevocationRegistry(regRes);
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : "Failed to load federation data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const activeIssuer = issuers.find((i) => i.issuer_id === selectedIssuerId) ?? issuers[0];

  const handleRevokeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!revokingCredId) return;
    setIsSubmittingRevoke(true);
    setActionError(null);
    try {
      const res = await api.revokeFederatedCredential({
        credential_id: revokingCredId,
        issuer_id: selectedIssuerId,
        reason: revokeReason,
        reason_description: revokeNotes || `Revoked by ${activeIssuer?.name || "Issuer"} (${revokeReason})`,
        operator_id: "OFFICER-DEMO-01",
      });
      setActionSuccess(`Credential ${revokingCredId} successfully revoked and published to Revocation Registry.`);
      setRevokingCredId(null);
      setRevokeNotes("");
      await loadData();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : "Failed to revoke credential");
    } finally {
      setIsSubmittingRevoke(false);
    }
  };

  const handleIssueSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmittingIssue(true);
    setActionError(null);

    let claims: Record<string, unknown> = {};
    if (issueType === "CLASS_XII_MARKSHEET") {
      claims = {
        student_name: issueStudentName,
        roll_number: issueRollNo,
        percentage: parseFloat(issuePercentage) || 85.0,
        passed: true,
        year: 2024,
      };
    } else if (issueType === "INCOME_CERTIFICATE") {
      claims = {
        citizen_name: issueStudentName,
        annual_income_inr: parseInt(issueIncomeAmount, 10) || 450000,
        income_eligible: (parseInt(issueIncomeAmount, 10) || 450000) <= 800000,
        state: "NCT of Delhi",
        validity_year: "2026-2027",
      };
    } else if (issueType === "DRIVING_LICENSE") {
      claims = {
        holder_name: issueStudentName,
        license_number: issueLicenseNo,
        vehicle_class: "LMV_MCWG",
        issued_state: "Delhi",
        valid_until: "2044-08-20",
      };
    } else {
      claims = {
        holder_name: issueStudentName,
        credential_title: issueTitle,
        issued_date: new Date().toISOString().split("T")[0],
        verified: true,
      };
    }

    try {
      const res = await api.issueFederatedCredential({
        issuer_id: selectedIssuerId,
        citizen_account_id: issueCitizenId,
        credential_type: issueType,
        title: issueTitle,
        claims,
        validity_days: 365,
      });
      setActionSuccess(`Successfully minted sovereign credential ${res.credential.credential_id} with Ed25519 signature!`);
      setActiveTab("credentials");
      await loadData();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : "Failed to issue credential");
    } finally {
      setIsSubmittingIssue(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8 font-sans">
      {/* 1. Header Banner */}
      <div className="bg-gradient-to-br from-[#092F4F] via-[#0B5D9B] to-[#1D4ED8] text-white rounded-3xl p-8 shadow-xl relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 opacity-10 pointer-events-none">
          <span className="text-[180px]">🏛️</span>
        </div>
        <div className="relative z-10 space-y-3">
          <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-md px-3.5 py-1 rounded-full text-xs font-bold tracking-wide uppercase">
            <span>🛡️ Federated Trust Network</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span>Live Registry</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Government Issuer & Revocation Authority
          </h1>
          <p className="text-sm sm:text-base text-blue-100 max-w-2xl leading-relaxed">
            Mint cryptographically signed verifiable sovereign credentials and manage real-time cryptographic revocation status lists across accredited national authorities.
          </p>
        </div>
      </div>

      {/* 2. Notifications / Alerts */}
      {actionSuccess && (
        <div className="flex items-start justify-between bg-emerald-50 border border-emerald-300 text-emerald-900 rounded-2xl p-4 shadow-sm animate-fade-in">
          <div className="flex items-center gap-3">
            <span className="text-xl">✅</span>
            <div className="text-sm font-semibold">{actionSuccess}</div>
          </div>
          <button
            type="button"
            onClick={() => setActionSuccess(null)}
            className="text-emerald-700 hover:text-emerald-900 text-lg font-bold cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      {actionError && (
        <div className="flex items-start justify-between bg-rose-50 border border-rose-300 text-rose-900 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <span className="text-xl">⚠️</span>
            <div className="text-sm font-semibold">{actionError}</div>
          </div>
          <button
            type="button"
            onClick={() => setActionError(null)}
            className="text-rose-700 hover:text-rose-900 text-lg font-bold cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      {/* 3. Federated Authority Selector */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-lg font-extrabold text-slate-900">Select Accredited Issuing Authority</h2>
            <p className="text-xs text-slate-500">Switch authority context to manage credential issuance and revocation keys.</p>
          </div>
          <span className="text-xs font-semibold px-3 py-1 bg-slate-100 text-slate-700 rounded-full border border-slate-200">
            {issuers.length} Accredited Authorities
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {issuers.map((iss) => {
            const isSelected = iss.issuer_id === selectedIssuerId;
            return (
              <button
                key={iss.issuer_id}
                type="button"
                onClick={() => setSelectedIssuerId(iss.issuer_id)}
                className={`text-left p-4 rounded-2xl border-2 transition-all cursor-pointer flex flex-col justify-between ${
                  isSelected
                    ? "border-[#0B5D9B] bg-blue-50/60 shadow-md ring-2 ring-blue-500/20"
                    : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/50"
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold text-slate-500 tracking-wider uppercase">
                      {iss.issuer_id}
                    </span>
                    <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                      {iss.trust_score}% Trust
                    </span>
                  </div>
                  <div className="font-bold text-sm text-slate-900 line-clamp-1">{iss.name}</div>
                  <div className="text-xs text-slate-500 line-clamp-1">{iss.category} • {iss.jurisdiction}</div>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-slate-600">
                  <span>{iss.algorithm}</span>
                  <span className="font-medium text-blue-700">{iss.accreditation_level}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Selected Authority Metadata Card */}
        {activeIssuer && (
          <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200/80 flex flex-wrap items-center justify-between gap-4 text-xs">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-black text-lg">
                🏛️
              </div>
              <div>
                <div className="font-bold text-slate-900 text-sm">{activeIssuer.name}</div>
                <div className="text-slate-500 font-mono text-[11px]">
                  Endpoint: {activeIssuer.endpoint} | Key: {activeIssuer.public_key_id}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-md bg-blue-100 text-blue-800 font-semibold text-[11px]">
                {activeIssuer.accreditation_level}
              </span>
              <span className="px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800 font-semibold text-[11px]">
                Status: ACTIVE
              </span>
            </div>
          </div>
        )}
      </div>

      {/* 4. Action Tabs */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-200 pb-1">
          <button
            type="button"
            onClick={() => setActiveTab("credentials")}
            className={`px-5 py-2.5 text-sm font-bold rounded-xl transition-all cursor-pointer ${
              activeTab === "credentials"
                ? "bg-[#0B5D9B] text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            📋 Issued Credentials ({credentials.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("issue")}
            className={`px-5 py-2.5 text-sm font-bold rounded-xl transition-all cursor-pointer ${
              activeTab === "issue"
                ? "bg-[#0B5D9B] text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            ✨ Mint Verifiable Credential
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("registry")}
            className={`px-5 py-2.5 text-sm font-bold rounded-xl transition-all cursor-pointer ${
              activeTab === "registry"
                ? "bg-[#0B5D9B] text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            🛑 Dynamic Revocation Registry ({revocationRegistry?.revoked_count ?? 0})
          </button>
        </div>

        {/* Tab 1: Issued Credentials & Revocation Management */}
        {activeTab === "credentials" && (
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h3 className="text-base font-extrabold text-slate-900">Active Sovereign Credentials</h3>
                <p className="text-xs text-slate-500">
                  Manage issuance status and execute 1-click cryptographic revocations.
                </p>
              </div>
              <button
                type="button"
                onClick={loadData}
                className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 cursor-pointer"
              >
                🔄 Refresh Credentials
              </button>
            </div>

            {loading ? (
              <div className="text-center py-12 text-slate-400">
                <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
                <div>Loading federated credentials…</div>
              </div>
            ) : credentials.length === 0 ? (
              <div className="text-center py-12 text-slate-400 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                <div className="text-3xl mb-2">📄</div>
                <div className="font-semibold text-slate-600">No credentials found</div>
                <div className="text-xs text-slate-400 mt-1">Mint a new credential using the Mint tab above.</div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 text-[11px] font-bold text-slate-400 uppercase tracking-wider bg-slate-50/50">
                      <th className="py-3 px-4">Credential ID / Type</th>
                      <th className="py-3 px-4">Citizen Account</th>
                      <th className="py-3 px-4">Issuer</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {credentials.map((c) => {
                      const isRevoked = c.is_revoked || c.status === "REVOKED";
                      return (
                        <tr key={c.credential_id} className="hover:bg-slate-50/60 transition-colors">
                          <td className="py-3 px-4">
                            <div className="font-bold text-slate-900 font-mono text-xs">{c.credential_id}</div>
                            <div className="text-xs text-slate-500">{c.credential_type}</div>
                          </td>
                          <td className="py-3 px-4">
                            <span className="font-semibold text-slate-800">{c.account_id}</span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-xs font-medium text-slate-600">{c.issuer}</span>
                          </td>
                          <td className="py-3 px-4">
                            {isRevoked ? (
                              <span className="inline-flex items-center gap-1 text-xs font-extrabold px-2.5 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-200">
                                <span>⊘</span> REVOKED
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 text-xs font-extrabold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                                <span>✓</span> ACTIVE
                              </span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-right">
                            {!isRevoked ? (
                              <button
                                type="button"
                                onClick={() => setRevokingCredId(c.credential_id)}
                                className="px-3 py-1.5 text-xs font-bold rounded-lg bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 transition-all cursor-pointer"
                              >
                                🛑 Revoke
                              </button>
                            ) : (
                              <span className="text-xs text-slate-400 font-medium italic">
                                Revoked {c.revocation_details?.revoked_at ? new Date(c.revocation_details.revoked_at).toLocaleDateString() : ""}
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Mint New Verifiable Sovereign Credential */}
        {activeTab === "issue" && (
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm max-w-3xl mx-auto space-y-6">
            <div>
              <h3 className="text-xl font-extrabold text-slate-900">Mint New Verifiable Credential</h3>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Authoritatively sign and issue a sovereign credential using {activeIssuer?.name}&apos;s Ed25519 digital signature key.
              </p>
            </div>

            <form onSubmit={handleIssueSubmit} className="space-y-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Target Citizen Account
                  </label>
                  <select
                    value={issueCitizenId}
                    onChange={(e) => setIssueCitizenId(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
                  >
                    <option value="DIN-DEMO-001">DIN-DEMO-001 (Rahul Sharma - Default)</option>
                    <option value="DIN-DEMO-002">DIN-DEMO-002 (Priya Verma - Subsidies)</option>
                    <option value="DIN-DEMO-003">DIN-DEMO-003 (Amit Patel - Student)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Credential Schema Template
                  </label>
                  <select
                    value={issueType}
                    onChange={(e) => {
                      setIssueType(e.target.value);
                      if (e.target.value === "CLASS_XII_MARKSHEET") setIssueTitle("CBSE Senior School Certificate Examination");
                      else if (e.target.value === "INCOME_CERTIFICATE") setIssueTitle("Annual Income Assessment Certificate");
                      else if (e.target.value === "DRIVING_LICENSE") setIssueTitle("Permanent Motor Vehicle Driving License");
                      else setIssueTitle("University Degree & Official Transcript");
                    }}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
                  >
                    <option value="CLASS_XII_MARKSHEET">Academic Marksheet (Class XII)</option>
                    <option value="INCOME_CERTIFICATE">Income Certificate (Revenue Dept)</option>
                    <option value="DRIVING_LICENSE">Driving License (MoRTH / Parivahan)</option>
                    <option value="DEGREE_CERTIFICATE">Bachelor Degree Certificate (University)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Credential Title
                </label>
                <input
                  type="text"
                  value={issueTitle}
                  onChange={(e) => setIssueTitle(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
                  required
                />
              </div>

              {/* Dynamic Claim Fields Based on Type */}
              <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-4">
                <div className="text-xs font-bold text-slate-600 uppercase tracking-wide">
                  Structured Credential Claims
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Citizen Full Name</label>
                    <input
                      type="text"
                      value={issueStudentName}
                      onChange={(e) => setIssueStudentName(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
                    />
                  </div>

                  {issueType === "CLASS_XII_MARKSHEET" && (
                    <>
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1">Roll Number</label>
                        <input
                          type="text"
                          value={issueRollNo}
                          onChange={(e) => setIssueRollNo(e.target.value)}
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm bg-white"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1">Aggregate Marks (%)</label>
                        <input
                          type="number"
                          step="0.1"
                          value={issuePercentage}
                          onChange={(e) => setIssuePercentage(e.target.value)}
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm bg-white"
                        />
                      </div>
                    </>
                  )}

                  {issueType === "INCOME_CERTIFICATE" && (
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Annual Income (INR ₹)</label>
                      <input
                        type="number"
                        value={issueIncomeAmount}
                        onChange={(e) => setIssueIncomeAmount(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm bg-white"
                      />
                    </div>
                  )}

                  {issueType === "DRIVING_LICENSE" && (
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">License Number</label>
                      <input
                        type="text"
                        value={issueLicenseNo}
                        onChange={(e) => setIssueLicenseNo(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm bg-white"
                      />
                    </div>
                  )}
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isSubmittingIssue}
                  className="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-[#0B5D9B] to-[#1D4ED8] text-white font-extrabold text-sm shadow-md hover:shadow-lg transition-all cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isSubmittingIssue ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Signing & Minting Sovereign Credential…</span>
                    </>
                  ) : (
                    <>
                      <span>✍️ Mint & Sign Sovereign Credential (Ed25519)</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Tab 3: Dynamic Cryptographic Revocation Registry Explorer */}
        {activeTab === "registry" && (
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-lg font-extrabold text-slate-900">Cryptographic Revocation Registry</h3>
                <p className="text-xs text-slate-500">
                  Authoritative public status accumulator matching W3C Bitstring Status List & RFC 5280 CRL standards.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold bg-slate-100 text-slate-800 px-3 py-1 rounded-lg border border-slate-200">
                  Standard: W3C StatusList2021
                </span>
              </div>
            </div>

            {revocationRegistry && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-2xl bg-blue-50/50 border border-blue-200">
                  <div className="text-xs font-bold text-blue-700 uppercase tracking-wide">Registry Version</div>
                  <div className="text-lg font-black text-slate-900 mt-1">{revocationRegistry.registry_version}</div>
                </div>
                <div className="p-4 rounded-2xl bg-rose-50/50 border border-rose-200">
                  <div className="text-xs font-bold text-rose-700 uppercase tracking-wide">Revoked Count</div>
                  <div className="text-lg font-black text-slate-900 mt-1">{revocationRegistry.revoked_count} Credentials</div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                  <div className="text-xs font-bold text-slate-600 uppercase tracking-wide">Aggregate Digest</div>
                  <div className="text-xs font-mono font-bold text-slate-800 mt-1 truncate">
                    {revocationRegistry.aggregate_digest}
                  </div>
                </div>
              </div>
            )}

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-[11px] font-bold text-slate-400 uppercase tracking-wider bg-slate-50/50">
                    <th className="py-3 px-4">Revoked Credential ID</th>
                    <th className="py-3 px-4">Issuing Authority</th>
                    <th className="py-3 px-4">Reason Code</th>
                    <th className="py-3 px-4">Revocation Timestamp</th>
                    <th className="py-3 px-4">Operator</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {revocationRegistry?.revocations.map((rev) => (
                    <tr key={rev.credential_id} className="hover:bg-rose-50/30 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-xs text-rose-900">
                        {rev.credential_id}
                      </td>
                      <td className="py-3 px-4 text-xs font-semibold text-slate-700">
                        {rev.issuer_id}
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-xs font-extrabold px-2.5 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-200">
                          {rev.reason}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-500 font-mono">
                        {new Date(rev.revoked_at).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-600 font-medium">
                        {rev.operator_id}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* 5. 1-Click Revocation Confirmation Modal */}
      {revokingCredId && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl border border-slate-200 space-y-5 animate-scale-up">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center text-2xl font-black">
                🛑
              </div>
              <div>
                <h3 className="text-lg font-extrabold text-slate-900">Revoke Sovereign Credential</h3>
                <p className="text-xs text-slate-500">
                  Credential ID: <span className="font-mono font-bold text-slate-800">{revokingCredId}</span>
                </p>
              </div>
            </div>

            <form onSubmit={handleRevokeSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Revocation Reason Code
                </label>
                <select
                  value={revokeReason}
                  onChange={(e) => setRevokeReason(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold focus:ring-2 focus:ring-rose-500 focus:outline-hidden"
                >
                  <option value="SUSPECTED_FRAUD">SUSPECTED_FRAUD (Suspected Alteration / Discrepancy)</option>
                  <option value="DATA_CORRECTION_SUPERSEDED">DATA_CORRECTION_SUPERSEDED (Replaced by Corrected Record)</option>
                  <option value="HOLDER_REQUESTED">HOLDER_REQUESTED (Citizen Requested Revocation)</option>
                  <option value="EXPIRED">EXPIRED (Validity Period Elapsed)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Revocation Notes & Explanation
                </label>
                <textarea
                  rows={3}
                  value={revokeNotes}
                  onChange={(e) => setRevokeNotes(e.target.value)}
                  placeholder="Provide audit reason for credential revocation…"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-rose-500 focus:outline-hidden"
                />
              </div>

              <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-800 font-medium flex items-center gap-2">
                <span>⚠️</span>
                <span>
                  This action generates an immutable cryptographic revocation assertion and will immediately invalidate any presented proofs.
                </span>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setRevokingCredId(null)}
                  className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 text-sm font-bold hover:bg-slate-100 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingRevoke}
                  className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-sm font-extrabold shadow-md cursor-pointer disabled:opacity-50 flex items-center gap-2"
                >
                  {isSubmittingRevoke ? "Revoking…" : "Confirm Cryptographic Revocation"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
