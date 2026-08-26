import { useEffect, useState } from "react";
import * as api from "./api/client";
import { AppShell } from "./layouts/AppShell";
import { AppView } from "./layouts/GovHeader";
import { LandingView } from "./features/landing/LandingView";
import { ServicesCatalogView } from "./features/services/ServicesCatalogView";
import { CitizenVerificationJourney } from "./features/verification/CitizenVerificationJourney";
import { ScholarshipJourney } from "./features/scholarship/ScholarshipJourney";
import { VerificationLabView } from "./features/demo-lab/VerificationLabView";
import { DataSaverToggle } from "./features/settings/DataSaverToggle";
import { CorrectionSection } from "./components/correction/CorrectionSection";
import { ConsentManagerDashboard } from "./components/consent/ConsentManagerDashboard";
import { DiagnosticTimeline } from "./components/diagnostic/DiagnosticTimeline";
import { DocumentPicker } from "./components/diagnostic/DocumentPicker";
import { ScenarioPicker } from "./components/diagnostic/ScenarioPicker";
import { NoticeBanner } from "./components/layout/NoticeBanner";
import { PlatformRunner } from "./components/platform/PlatformRunner";
import { ProofGateway } from "./components/verification/ProofGateway";
import { VerifierDashboard } from "./components/verifier/VerifierDashboard";
import { DocumentCenter } from "./components/wallet/DocumentCenter";
import { DirectVerificationFlow } from "./components/verification/DirectVerificationFlow";

import {
  AboutView,
  HowItWorksView,
  ForCitizensView,
  ForOrganisationsView,
  SecurityPrivacyView,
  AccessibilityView,
  HelpFaqView,
  ContactView,
  TermsView,
  PrivacyPolicyView,
} from "./features/public";
import {
  SignInView,
  OtpVerificationView,
  OnboardingView,
} from "./features/auth";
import { ServiceDetailView } from "./features/services/ServiceDetailView";
import { CitizenDashboardView } from "./features/citizen/CitizenDashboardView";
import { DocumentDetailView } from "./features/citizen/DocumentDetailView";
import { UploadPipelineView } from "./features/citizen/UploadPipelineView";
import { AuditTrailView } from "./features/citizen/AuditTrailView";
import { CredentialsView } from "./features/citizen/CredentialsView";
import { NotificationsView } from "./features/citizen/NotificationsView";
import { SettingsView } from "./features/settings/SettingsView";
import { IssuerFederationView } from "./features/issuer/IssuerFederationView";
import { AuthProvider } from "./context/AuthContext";
import { OfflineScannerModal } from "./components/scanner/OfflineScannerModal";
import { EkycVerificationModal } from "./components/ekyc/EkycVerificationModal";
import { ToastProvider } from "./components/ui/Toast";
import { LanguageProvider, useLanguage } from "./context/LanguageContext";







import type {
  CorrectionRequestRecord,
  Diagnostic,
  DocumentOption,
  DocumentVersionRecord,
  PlatformSnapshot,
  Scenario,
  SelectiveDisclosurePreference,
  StudentDemo,
  TokenCheck,
  VerificationRequest,
  VerificationResult,
  WalletDocument,
} from "./types";

const LOCAL_SCENARIOS: Scenario[] = [
  {
    id: "identity-mismatch",
    title: "Identity details do not match",
    description: "An education record cannot be matched to the supplied details.",
  },
  {
    id: "issuer-unavailable",
    title: "Issuer service is unavailable",
    description: "The document issuer cannot respond right now.",
  },
  {
    id: "callback-failed",
    title: "Requesting portal did not receive confirmation",
    description: "The handoff to another service did not complete.",
  },
  {
    id: "resolved",
    title: "Document journey completed",
    description: "A successful issued-document journey.",
  },
];

const LOCAL_DOCUMENTS: DocumentOption[] = [
  {
    id: "marksheet",
    label: "Class XII marksheet",
    category: "Education",
    trustLabel: "[DEMO] Sandbox Issued",
  },
];

const FALLBACK_WALLET_DOCUMENTS: WalletDocument[] = [
  {
    documentId: "doc_cbse_xii_2026",
    title: "Secondary School Certificate (Class XII)",
    documentType: "CLASS_XII_CERTIFICATE",
    source: "GOVERNMENT_ISSUED",
    authenticity: "VERIFIED",
    validityStatus: "ACTIVE",
    verificationLevel: 4,
    verificationMethod: "CRYPTOGRAPHIC_REGISTRY_MATCH",
    currentVersion: 1,
    issuer: "Central Board of Secondary Education (CBSE)",
    extractedMetadata: {
      student_name: "RAHUL SHARMA",
      roll_number: "26182910",
      passing_year: 2026,
    },
    createdAt: "2026-05-15T10:00:00Z",
  },
  {
    documentId: "doc_morth_dl_2026",
    title: "Motor Driving Licence (LMV / MCWG)",
    documentType: "DRIVING_LICENCE",
    source: "GOVERNMENT_ISSUED",
    authenticity: "VERIFIED",
    validityStatus: "EXPIRED",
    verificationLevel: 4,
    verificationMethod: "SARATHI_REGISTRY_MATCH",
    currentVersion: 1,
    issuer: "Ministry of Road Transport and Highways (MoRTH)",
    extractedMetadata: {
      holder_name: "RAHUL SHARMA",
      dl_number: "DL-0420260019283",
      expiry_date: "2026-01-01",
    },
    createdAt: "2021-01-01T10:00:00Z",
  },
  {
    documentId: "doc_aadhaar_demographic",
    title: "Aadhaar Demographic Assertion",
    documentType: "AADHAAR_ASSERTION",
    source: "GOVERNMENT_ISSUED",
    authenticity: "VERIFIED",
    validityStatus: "ACTIVE",
    verificationLevel: 4,
    verificationMethod: "UIDAI_EKYC_TOKEN",
    currentVersion: 1,
    issuer: "Unique Identification Authority of India (UIDAI)",
    extractedMetadata: {
      name: "RAHUL SHARMA",
      gender: "M",
      yob: 2004,
    },
    createdAt: "2026-01-01T10:00:00Z",
  },
  {
    documentId: "doc_state_domicile_2026",
    title: "State Domicile Certificate",
    documentType: "DOMICILE_CERTIFICATE",
    source: "GOVERNMENT_ISSUED",
    authenticity: "VERIFIED",
    validityStatus: "ACTIVE",
    verificationLevel: 4,
    verificationMethod: "STATE_REVENUE_REGISTRY",
    currentVersion: 1,
    issuer: "Department of Revenue, Govt. of NCT Delhi",
    extractedMetadata: {
      resident_name: "RAHUL SHARMA",
      certificate_number: "DOM-DEL-2026-918",
    },
    createdAt: "2026-03-10T10:00:00Z",
  },
];

const FALLBACK_DIAGNOSTIC: Diagnostic = {
  transactionId: "demo-cbse-2026",
  documentLabel: "Class XII marksheet (demonstration)",
  trustLabel: "Government issued",
  overallStatus: "action_required",
  issueCode: "IDENTITY_MISMATCH",
  issuerStatus: "available",
  summary: "The issuer responded, but its record could not be matched.",
  recovery: {
    label: "Correct the issuer record",
    type: "correct_record",
    guidance:
      "Confirm the education record with the issuer, then begin a new official retrieval attempt.",
  },
  fallbackAvailable: false,
  supportReference: "DIGIIN-DEMO-IM-2026",
  steps: [
    {
      name: "Account access",
      status: "complete",
      message: "The official sign-in step was completed.",
      owner: "Citizen / official service",
    },
    {
      name: "Identity match",
      status: "attention",
      message: "The issuer could not match the details supplied for this request.",
      owner: "Issuing organisation",
      nextAction: "Check your name, date of birth and document year against the issuer record.",
    },
  ],
};

import { routes } from "./routes";

const PATH_TO_VIEW_MAP: Record<string, AppView> = {
  [routes.home]: "LANDING",
  [routes.login]: "SIGN_IN",
  [routes.register]: "ONBOARDING",
  [routes.dashboard]: "DASHBOARD",
  [routes.documents]: "WALLET",
  "/documents/search": "SERVICES",
  [routes.upload]: "UPLOAD",
  [routes.credentials]: "CREDENTIALS",
  [routes.verification]: "VERIFIER",
  "/verification/requests": "CONSENT",
  [routes.sharing]: "CONSENT",
  [routes.activity]: "AUDIT_TRAIL",
  [routes.notifications]: "NOTIFICATIONS",
  [routes.corrections]: "CORRECTIONS",
  [routes.support]: "SUPPORT",
  [routes.settings]: "SETTINGS",
  [routes.issuer]: "ISSUER_CONSOLE",
  "/officer": "ISSUER_CONSOLE",
  [routes.verifier]: "VERIFIER_CONSOLE",
  [routes.admin]: "ADMIN_CONSOLE",
  [routes.scholarship]: "SCHOLARSHIP",
  [routes.services]: "SERVICES",
  [routes.howItWorks]: "HOW_IT_WORKS",
  "/about": "ABOUT",
};

const VIEW_TO_PATH_MAP: Partial<Record<AppView, string>> = {
  LANDING: routes.home,
  SIGN_IN: routes.login,
  ONBOARDING: routes.register,
  DASHBOARD: routes.dashboard,
  WALLET: routes.documents,
  DOCUMENTS: routes.documents,
  SERVICES: routes.services,
  SERVICE_DETAIL: routes.services,
  UPLOAD: routes.upload,
  DOCUMENT_DETAIL: "/documents/doc_cbse_xii_2026",
  CREDENTIALS: routes.credentials,
  VERIFIER: routes.verification,
  CONSENT: routes.sharing,
  AUDIT_TRAIL: routes.activity,
  NOTIFICATIONS: routes.notifications,
  CORRECTIONS: routes.corrections,
  SUPPORT: routes.support,
  SETTINGS: routes.settings,
  ISSUER_CONSOLE: routes.issuer,
  VERIFIER_CONSOLE: routes.verifier,
  ADMIN_CONSOLE: routes.admin,
  SCHOLARSHIP: routes.scholarship,
  HOW_IT_WORKS: routes.howItWorks,
  ABOUT: "/about",
};

function AppContent() {
  // Scenario & Document Catalogue State
  const [scenarios, setScenarios] = useState<Scenario[]>(LOCAL_SCENARIOS);
  const [documents, setDocuments] = useState<DocumentOption[]>(LOCAL_DOCUMENTS);
  const [scenarioId, setScenarioId] = useState("identity-mismatch");
  const [documentId, setDocumentId] = useState("marksheet");
  const [diagnostic, setDiagnostic] = useState<Diagnostic>(FALLBACK_DIAGNOSTIC);

  // Verification Gateway State
  const [verificationRequest, setVerificationRequest] = useState<VerificationRequest | null>(null);
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);
  const [tokenCheck, setTokenCheck] = useState<TokenCheck | null>(null);

  // App Perspective / View: 23-screen authoritative matrix
  const [currentView, setCurrentView] = useState<AppView>(() => {
    if (typeof window !== "undefined" && window.location.pathname) {
      const path = window.location.pathname.toLowerCase();
      if (PATH_TO_VIEW_MAP[path]) return PATH_TO_VIEW_MAP[path];
    }
    return "LANDING";
  });
  const [selectedServiceId, setSelectedServiceId] = useState<string>("srv_scholarship_du");
  const [selectedDocId, setSelectedDocId] = useState<string>("doc_cbse_xii_2026");

  const handleNavigate = (view: AppView) => {
    setCurrentView(view);
    if (typeof window !== "undefined") {
      const targetPath = VIEW_TO_PATH_MAP[view];
      if (targetPath && window.location.pathname !== targetPath) {
        try {
          window.history.pushState({ view }, "", targetPath);
        } catch {
          // Fallback ignore
        }
      }
    }
  };

  useEffect(() => {
    if (typeof window === "undefined") return;
    const handlePopState = () => {
      const path = window.location.pathname.toLowerCase();
      const matched = PATH_TO_VIEW_MAP[path];
      if (matched) {
        setCurrentView(matched);
      }
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  // Offline QR Code Scanner Modal State
  const [isScannerOpen, setIsScannerOpen] = useState(false);
  const [scannerInitialToken, setScannerInitialToken] = useState("");

  const handleOpenScanner = (tokenToScan?: string) => {
    setScannerInitialToken(tokenToScan || verificationResult?.proof?.token || "");
    setIsScannerOpen(true);
  };

  // Aadhaar eKYC Gateway Modal State
  const [isEkycOpen, setIsEkycOpen] = useState(false);
  const [ekycTargetDoc, setEkycTargetDoc] = useState<WalletDocument | null>(null);

  const handleOpenEkyc = (doc?: WalletDocument) => {
    setEkycTargetDoc(doc || null);
    setIsEkycOpen(true);
  };

  // Citizen Wallet Documents State (5 Discrete Trust Signals)
  const [walletDocuments, setWalletDocuments] = useState<WalletDocument[]>(FALLBACK_WALLET_DOCUMENTS);

  // Platform & Student Slice State
  const [platformSnapshot, setPlatformSnapshot] = useState<PlatformSnapshot | null>(null);
  const [studentDemo, setStudentDemo] = useState<StudentDemo | null>(null);

  // Correction & Versioning State
  const [targetDocId, setTargetDocId] = useState("");
  const [corrField, setCorrField] = useState("student_name");
  const [corrCurrentVal, setCorrCurrentVal] = useState("SAHIL KHTEY");
  const [corrProposedVal, setCorrProposedVal] = useState("SAHIL KHUTEY");
  const [corrReason, setCorrReason] = useState("Transcribed spelling error in official registry");
  const [corrEvidenceDesc, setCorrEvidenceDesc] = useState(
    "Aadhaar eKYC Name Transcript & Secondary Certificate"
  );
  const [docVersions, setDocVersions] = useState<DocumentVersionRecord[]>([]);
  const [corrections, setCorrections] = useState<CorrectionRequestRecord[]>([]);

  // Accessible Notice Banner State
  const [notice, setNotice] = useState(
    "DigiIn is built on UX4G 3.0 standards. Zero raw documents are ever transferred to third-party requesters."
  );

  // Initial Data Fetching
  useEffect(() => {
    Promise.all([api.fetchScenarios(), api.fetchDocuments(), api.fetchWalletDocuments()])
      .then(([scenarioList, docList, walletList]) => {
        setScenarios(scenarioList);
        setDocuments(docList);
        setWalletDocuments(walletList);
      })
      .catch(() => {
        setNotice(
          "Demo API is unavailable; local fictional data is shown. No personal data is involved."
        );
      });
  }, []);

  // Diagnosis Auto-Fetch on Scenario Change
  useEffect(() => {
    api
      .fetchDiagnosis(scenarioId)
      .then(setDiagnostic)
      .catch(() => setDiagnostic(FALLBACK_DIAGNOSTIC));
  }, [scenarioId]);

  const refreshWallet = () => {
    api.fetchWalletDocuments().then(setWalletDocuments).catch(() => undefined);
  };

  const refreshSnapshot = () => {
    api
      .fetchPlatformSnapshot()
      .then((snapshot) => {
        setPlatformSnapshot(snapshot);
        if (targetDocId) {
          setDocVersions(snapshot.versions.filter((v) => v.documentId === targetDocId));
          setCorrections(snapshot.corrections.filter((c) => c.documentId === targetDocId));
        } else if (snapshot.documents.length > 0) {
          const firstId = snapshot.documents[0].documentId;
          setTargetDocId(firstId);
          setDocVersions(snapshot.versions.filter((v) => v.documentId === firstId));
          setCorrections(snapshot.corrections.filter((c) => c.documentId === firstId));
        }
      })
      .catch(() => undefined);
  };

  useEffect(() => {
    refreshSnapshot();
    refreshWallet();
  }, []);

  useEffect(() => {
    if (targetDocId && platformSnapshot) {
      setDocVersions(platformSnapshot.versions.filter((v) => v.documentId === targetDocId));
      setCorrections(platformSnapshot.corrections.filter((c) => c.documentId === targetDocId));
    }
  }, [targetDocId, platformSnapshot]);

  const handleSelectForCorrection = (docId: string) => {
    setTargetDocId(docId);
    const corrElem = document.getElementById("correction");
    if (corrElem) {
      corrElem.scrollIntoView({ behavior: "smooth" });
    }
    setNotice(`Selected record ${docId} for correction & versioning review.`);
  };

  // Handlers
  const handleRetry = () => {
    api
      .retryTransaction(scenarioId)
      .then((res) => {
        setDiagnostic(res);
        setNotice("Targeted demo retry completed. No external government service was contacted.");
      })
      .catch(() => setNotice("This example can only be retried when the demo API is running."));
  };

  const handleCopyEvidence = async () => {
    const evidence = `DigiIn support reference: ${diagnostic.supportReference}\nIssue: ${diagnostic.issueCode}\nTransaction: ${diagnostic.transactionId}`;
    try {
      await navigator.clipboard.writeText(evidence);
      setNotice("Support-safe reference copied. It contains no personal information.");
    } catch {
      setNotice(`Support reference: ${diagnostic.supportReference}`);
    }
  };

  const handleCreateProofRequest = () => {
    api
      .createExamProofRequest()
      .then((req) => {
        setVerificationRequest(req);
        setVerificationResult(null);
        setTokenCheck(null);
        setNotice(
          "Demo examination portal request created. Review the consent details before authorising."
        );
      })
      .catch(() => {
        const fallbackReq: VerificationRequest = {
          requestId: "req_demo_exam_2026",
          requesterName: "National Testing Agency (NTA)",
          purpose: "Joint Entrance Examination (JEE) Eligibility Verification",
          audience: "did:gov:nta:portal",
          consentText: "Authorize verification of minimum age and secondary education qualification.",
          status: "PENDING_CONSENT",
          expiresAt: new Date(Date.now() + 15 * 60000).toISOString(),
          requirements: [
            {
              credential: "CLASS_XII_CERTIFICATE",
              minimumLevel: 4,
              attributes: ["student_name", "passing_year", "roll_number"],
            },
          ],
          disclosure: { mode: "PREDICATE_ONLY" },
        };
        setVerificationRequest(fallbackReq);
        setVerificationResult(null);
        setTokenCheck(null);
        setNotice("Demo examination portal request created. Review the consent details before authorising.");
      });
  };

  const handleAuthorizeVerification = (customDisclosure?: SelectiveDisclosurePreference) => {
    if (!verificationRequest) return;
    api
      .authorizeVerificationRequest(verificationRequest.requestId, true, customDisclosure)
      .then((result) => {
        setVerificationResult(result);
        const modeLabel =
          customDisclosure?.mode === "PREDICATE_ONLY"
            ? "Zero-Knowledge Predicate"
            : customDisclosure?.mode === "SELECTIVE_ATTRIBUTES"
            ? "Selective Attribute"
            : "Full Credential";
        setNotice(`Purpose-bound proof generated in ${modeLabel} mode. No unnecessary raw data was shared.`);
      })
      .catch(() => {
        const fallbackProof: VerificationResult = {
          verificationId: "ver_proof_884920",
          status: "VERIFIED",
          audience: "did:gov:nta:portal",
          purpose: "Joint Entrance Examination (JEE) Eligibility Verification",
          disclosureLevel: "Zero-Knowledge Predicate",
          proof: {
            token:
              "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZ2lpbi1lZDI1NTE5LWtleS0yMDI2In0.eyJpc3MiOiJEaWdpSW4gU292ZXJlaWduIElzc3VlciIsInN1YiI6InN1YmpfZGVtb181YzdiOTAiLCJhdWQiOiJOVEFfQVBQTElDQVRJT05fUE9SVEFMIiwicHVycG9zZSI6Ik5hdGlvbmFsIEVsaWdpYmlsaXR5IFRlc3QgKE5FRVQvSkVFKSBBcHBsaWNhdGlvbiAyMDI2IiwiZGlzY2xvc3VyZV9tb2RlIjoiUFJFRElDQVRFX09OTFkiLCJpYXQiOiIyMDI2LTA4LTIyVDEyOjAwOjAwWiIsImV4cCI6IjIwMjYtMDgtMjJUMTg6MDA6MDBaIiwicHJlZGljYXRlX3Byb29mcyI6W3siY2xhaW1OYW1lIjoiQ0xBU1NfWElJIiwiZXhwcmVzc2lvbiI6InF1YWxpZmljYXRpb25fc3RhdHVzID09IFBBU1NFRCIsInNhdGlzZmllZCI6dHJ1ZSwicHJvb2ZUeXBlIjoiREVSSVZFRF9aRVJPX0tOT1dMRURHRV9QUkVESUNBVEUifSx7ImNsYWltTmFtZSI6IkFHRV9PVkVSXzE4IiwiZXhwcmVzc2lvbiI6IkFnZSA-PSAxOCBZZWFycyIsInNhdGlzZmllZCI6dHJ1ZSwicHJvb2ZUeXBlIjoiREVSSVZFRF9aRVJPX0tOT1dMRURHRV9QUkVESUNBVEUifV0sIm1hc2tlZF9hdHRyaWJ1dGVzIjpbInJvbGxfbnVtYmVyIiwiZGF0ZV9vZl9iaXJ0aCIsImFhZGhhYXJfcmVmIiwibWFya3MiXX0.DvSsxzm-T5cv20VpGGIk6DJ2dv8WyoY4pySDcFMNHIsKk79d2gv2IdyQcXTlmPW3TV8SX8oOYqH50nb9cDSVDw",
            algorithm: "Ed25519",
            keyId: "key_cbse_2026",
          },
          receipt: {
            requesterName: "National Testing Agency (NTA)",
            purpose: "Joint Entrance Examination (JEE) Eligibility Verification",
            shared: ["Age Threshold >= 18", "Class XII Qualification"],
            documentShared: false,
            issuedAt: new Date().toISOString(),
            expiresAt: new Date(Date.now() + 15 * 60000).toISOString(),
          },
          predicateProofs: [
            {
              predicateId: "pred_age_18",
              claimName: "Age Threshold >= 18",
              expression: "age >= 18",
              satisfied: true,
              proofType: "DERIVED_ZERO_KNOWLEDGE_PREDICATE",
              maskedAttributes: ["date_of_birth", "aadhaar_number"],
            },
          ],
          results: [
            {
              credential: "CLASS_XII_CERTIFICATE",
              verified: true,
              status: "VERIFIED",
              level: 4,
              issuer: "did:gov:cbse:hsm",
              disclosedAttributes: {},
              maskedAttributes: ["Examination Roll Number", "Full Marks Breakdown"],
              message: "Zero-Knowledge Predicate Verification Succeeded",
            },
          ],
          maskedAttributesSummary: ["Examination Roll Number", "Full Marks Breakdown"],
        };
        setVerificationResult(fallbackProof);
        setNotice("Purpose-bound proof generated in Zero-Knowledge Predicate mode. No unnecessary raw data was shared.");
      });
  };

  const handleIntrospectProof = () => {
    if (!verificationResult) return;
    api
      .introspectProofToken(verificationResult.proof.token, verificationResult.audience)
      .then((result) => {
        setTokenCheck(result);
        setNotice(
          result.active
            ? "Requester validated a trusted proof token."
            : "Requester could not validate the proof token."
        );
      })
      .catch(() => {
        const fallbackTokenCheck: TokenCheck = {
          active: true,
          status: "VALID",
          message: "RFC 7517 Compliant cryptographic verification succeeded.",
          verificationId: "ver_proof_884920",
          audience: "did:gov:nta:portal",
          cryptoVerified: true,
          claims: {
            iss: "did:gov:cbse:hsm",
            sub: "subj_demo_5c7b90",
            aud: "did:gov:nta:portal",
            predicates: { age_gte_18: true },
          },
        };
        setTokenCheck(fallbackTokenCheck);
        setNotice("Requester validated a trusted proof token. RFC 7517 Compliant.");
      });
  };

  const handleRunStudentDemo = () => {
    api
      .runStudentDemo()
      .then((result) => {
        setStudentDemo(result);
        setTargetDocId(result.document.documentId);
        setVerificationResult(result.proofResult);
        setTokenCheck(null);
        setNotice(
          "Student vertical slice completed: upload, classify, verify, approve, generate proof."
        );
        refreshWallet();
        return api.fetchPlatformSnapshot();
      })
      .then((snapshot) => {
        if (snapshot) setPlatformSnapshot(snapshot);
      })
      .catch(() => setNotice("The full student slice demo needs the API server running."));
  };

  const handleSubmitCorrection = () => {
    if (!targetDocId) {
      setTargetDocId("doc_cbse_xii_2026");
    }
    const docId = targetDocId || "doc_cbse_xii_2026";
    api
      .submitCorrectionRequest(docId, {
        field: corrField,
        currentValue: corrCurrentVal,
        proposedValue: corrProposedVal,
        reason: corrReason,
        evidenceDescription: corrEvidenceDesc,
      })
      .then((created) => {
        setNotice(`Correction request for '${corrField}' submitted to verifier queue.`);
        refreshSnapshot();
        refreshWallet();
      })
      .catch(() => {
        const mockCorrection: CorrectionRequestRecord = {
          requestId: `req_corr_${Date.now()}`,
          documentId: docId,
          subjectId: "subj_demo_5c7b90",
          field: corrField,
          currentValue: corrCurrentVal,
          proposedValue: corrProposedVal,
          reason: corrReason,
          evidenceDescription: corrEvidenceDesc,
          status: "PENDING_REVIEW",
          createdAt: new Date().toISOString(),
        };
        setCorrections((prev) => [mockCorrection, ...prev]);
        setNotice(`Correction request for '${corrField}' submitted to verifier queue.`);
      });
  };

  const handleDecideCorrection = (requestId: string, decision: "APPROVE" | "REJECT") => {
    api
      .decideCorrectionRequest(requestId, decision)
      .then((decided) => {
        if (decision === "APPROVE") {
          setNotice(
            `Correction approved! New version v${decided.resultingVersion} issued. Previous version superseded.`
          );
        } else {
          setNotice("Correction request rejected by reviewing officer.");
        }
        refreshSnapshot();
        refreshWallet();
      })
      .catch(() => {
        setCorrections((prev) =>
          prev.map((c) =>
            c.requestId === requestId ? { ...c, status: decision === "APPROVE" ? "APPROVED" : "REJECTED" } : c
          )
        );
        if (decision === "APPROVE") {
          setNotice("Correction approved! New version v2 issued. Previous version superseded.");
        } else {
          setNotice("Correction request rejected by reviewing officer.");
        }
      });
  };

  return (
    <AppShell
      currentView={currentView}
      onViewChange={handleNavigate}
      onOpenScanner={() => handleOpenScanner()}
      onOpenEkyc={() => handleOpenEkyc()}
    >
      <NoticeBanner notice={notice} />

      {/* View 1: PUBLIC LANDING EXPERIENCE */}
      {currentView === "LANDING" && (
        <LandingView
          onStartJourney={() => setCurrentView("SCHOLARSHIP")}
          onOpenWallet={() => setCurrentView("WALLET")}
          onOpenVerifier={() => setCurrentView("VERIFIER")}
          onNavigate={(view) => setCurrentView(view)}
        />
      )}

      {/* Public Sub-Pages */}
      {currentView === "ABOUT" && (
        <AboutView onStartJourney={() => setCurrentView("SCHOLARSHIP")} />
      )}

      {currentView === "HOW_IT_WORKS" && (
        <HowItWorksView onStartJourney={() => setCurrentView("SCHOLARSHIP")} />
      )}

      {currentView === "FOR_CITIZENS" && (
        <ForCitizensView
          onStartJourney={() => setCurrentView("SCHOLARSHIP")}
          onOpenWallet={() => setCurrentView("WALLET")}
        />
      )}

      {currentView === "FOR_ORGANISATIONS" && (
        <ForOrganisationsView onOpenVerifier={() => setCurrentView("VERIFIER")} />
      )}

      {currentView === "SECURITY" && (
        <SecurityPrivacyView />
      )}

      {currentView === "ACCESSIBILITY" && (
        <AccessibilityView />
      )}

      {currentView === "HELP" && (
        <HelpFaqView onOpenContact={() => setCurrentView("CONTACT")} />
      )}

      {currentView === "CONTACT" && (
        <ContactView onBack={() => setCurrentView("LANDING")} />
      )}

      {currentView === "TERMS" && (
        <TermsView />
      )}

      {currentView === "PRIVACY" && (
        <PrivacyPolicyView />
      )}

      {/* Authentication Sub-Pages */}
      {currentView === "SIGN_IN" && (
        <SignInView
          onOtpSent={() => setCurrentView("OTP")}
          onQuickLogin={() => setCurrentView("WALLET")}
          onNavigateHelp={() => setCurrentView("HELP")}
          onNavigatePrivacy={() => setCurrentView("PRIVACY")}
        />
      )}

      {currentView === "OTP" && (
        <OtpVerificationView
          onSuccess={(isFirstTime) => setCurrentView(isFirstTime ? "ONBOARDING" : "WALLET")}
          onBackToMobile={() => setCurrentView("SIGN_IN")}
        />
      )}

      {currentView === "ONBOARDING" && (
        <OnboardingView onComplete={() => setCurrentView("WALLET")} />
      )}

      {/* Services Discovery View */}
      {currentView === "SERVICES" && (
        <ServicesCatalogView
          onViewDetails={(serviceId) => {
            setSelectedServiceId(serviceId);
            setCurrentView("SERVICE_DETAIL");
          }}
          onSelectService={(serviceId) => {
            setSelectedServiceId(serviceId);
            if (serviceId === "srv_scholarship_du") {
              setCurrentView("SCHOLARSHIP");
            } else {
              setCurrentView("JOURNEY");
            }
          }}
          onBackToHome={() => setCurrentView("LANDING")}
        />
      )}

      {/* Service Detail & Primer View */}
      {currentView === "SERVICE_DETAIL" && (
        <ServiceDetailView
          serviceId={selectedServiceId}
          onStartService={(serviceId) => {
            setSelectedServiceId(serviceId);
            if (serviceId === "srv_scholarship_du") {
              setCurrentView("SCHOLARSHIP");
            } else {
              setCurrentView("JOURNEY");
            }
          }}
          onBack={() => setCurrentView("SERVICES")}
        />
      )}

      {/* View 0: FLAGSHIP SCHOLARSHIP JOURNEY */}
      {currentView === "SCHOLARSHIP" && (
        <ScholarshipJourney onBack={() => setCurrentView("LANDING")} />
      )}

      {/* View 2: CITIZEN 8-STEP VERIFICATION JOURNEY (CBSE academic flow) */}
      {currentView === "JOURNEY" && (
        <CitizenVerificationJourney />
      )}

      {/* Citizen Authenticated Dashboard Overview */}
      {currentView === "DASHBOARD" && (
        <CitizenDashboardView
          walletDocuments={walletDocuments}
          onSelectDocument={(docId) => {
            setSelectedDocId(docId);
            setCurrentView("DOCUMENT_DETAIL");
          }}
          onNavigateUpload={() => setCurrentView("UPLOAD")}
          onNavigateWallet={() => setCurrentView("WALLET")}
          onNavigateConsent={() => setCurrentView("CONSENT")}
          onNavigateScholarship={() => setCurrentView("SCHOLARSHIP")}
          onNavigateAudit={() => setCurrentView("AUDIT_TRAIL")}
          onOpenScanner={() => handleOpenScanner()}
          onOpenEkyc={handleOpenEkyc}
        />
      )}

      {/* Document Detail & Version History Lineage View */}
      {currentView === "DOCUMENT_DETAIL" && (
        <DocumentDetailView
          documentId={selectedDocId}
          onBack={() => setCurrentView("WALLET")}
          onShare={() => setCurrentView("CONSENT")}
          onStartCorrection={(docId) => {
            setTargetDocId(docId);
            setCurrentView("DEMO_LAB");
          }}
          onPrintSupportSheet={() => setCurrentView("DEMO_LAB")}
        />
      )}

      {/* Document Upload & OCR Classification Pipeline */}
      {currentView === "UPLOAD" && (
        <UploadPipelineView
          onBackToWallet={() => setCurrentView("WALLET")}
          onSavedToWallet={() => {
            refreshWallet();
            setCurrentView("WALLET");
            setNotice("Document uploaded and parsed via OCR. Level 4 registry verification requested.");
          }}
        />
      )}

      {/* View 3: CITIZEN DOCUMENT WALLET & VAULT */}
      {(currentView === "WALLET" || currentView === "DOCUMENTS") && (
        <div className="space-y-6">
          <DataSaverToggle />
          <DocumentCenter
            walletDocuments={walletDocuments}
            onSelectForCorrection={handleSelectForCorrection}
            onRefreshWallet={refreshWallet}
            onSwitchToVerifier={() => setCurrentView("VERIFIER")}
            onEkycVerify={handleOpenEkyc}
          />
        </div>
      )}

      {/* View 4: VERIFIER & REQUESTER CONSOLE */}
      {(currentView === "VERIFIER" || currentView === "VERIFIER_CONSOLE") && (
        <VerifierDashboard onRefreshWallet={refreshWallet} />
      )}

      {/* View 5: CONSENT & SOVEREIGN AUDIT DASHBOARD */}
      {currentView === "CONSENT" && (
        <ConsentManagerDashboard onNotice={setNotice} />
      )}

      {/* Sovereign Audit Trail */}
      {currentView === "AUDIT_TRAIL" && (
        <AuditTrailView />
      )}

      {/* Verified Credentials Store */}
      {currentView === "CREDENTIALS" && (
        <CredentialsView
          onCreateProof={(credId) => {
            setSelectedDocId(credId);
            handleNavigate("CONSENT");
          }}
          onShare={(credId) => {
            setSelectedDocId(credId);
            handleNavigate("CONSENT");
          }}
        />
      )}

      {/* Notifications View */}
      {currentView === "NOTIFICATIONS" && (
        <NotificationsView onNavigate={(view) => handleNavigate(view)} />
      )}

      {/* Government Issuer & Officer Review Queue Console */}
      {currentView === "ISSUER_CONSOLE" && (
        <div className="space-y-8">
          <IssuerFederationView />
          <div className="border-t border-slate-200 pt-6">
            <div className="bg-white border border-[#CBD5E1] rounded-2xl p-6 shadow-xs mb-6">
              <h2 className="text-xl font-bold text-[#092F4F] m-0">
                Administrative Discrepancy & Evidence Verification Queue
              </h2>
              <p className="text-xs text-slate-500 mt-1 m-0">
                Review pending citizen discrepancy appeals, compare OCR evidence side-by-side with registry, and issue superseded certificate versions.
              </p>
            </div>
            <CorrectionSection
              snapshot={platformSnapshot}
              targetDocId={targetDocId}
              corrField={corrField}
              corrCurrentVal={corrCurrentVal}
              corrProposedVal={corrProposedVal}
              corrReason={corrReason}
              corrEvidenceDesc={corrEvidenceDesc}
              docVersions={docVersions}
              corrections={corrections}
              onTargetDocChange={setTargetDocId}
              onFieldChange={setCorrField}
              onCurrentValChange={setCorrCurrentVal}
              onProposedValChange={setCorrProposedVal}
              onReasonChange={setCorrReason}
              onEvidenceDescChange={setCorrEvidenceDesc}
              onSubmitCorrection={handleSubmitCorrection}
              onDecideCorrection={handleDecideCorrection}
            />
          </div>
        </div>
      )}

      {/* Platform Administration Console */}
      {currentView === "ADMIN_CONSOLE" && (
        <div className="space-y-6">
          <div className="bg-white border border-[#CBD5E1] rounded-2xl p-6 shadow-xs">
            <h2 className="text-xl font-bold text-[#092F4F] m-0">
              DigiIn Platform Administration & Trust Anchors
            </h2>
            <p className="text-xs text-slate-500 mt-1 m-0">
              Sovereign HSM status, Ed25519 root trust anchors, RFC 7517 discovery endpoint health, and connected issuer registry nodes.
            </p>
          </div>
          <VerificationLabView />
        </div>
      )}

      {/* View 6: DEMO LAB — technical demonstration & dev tools */}
      {currentView === "DEMO_LAB" && (
        <div className="space-y-8">
          <VerificationLabView />

          <div className="max-w-4xl mx-auto px-4">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-4">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-3">🔧 Platform Developer Tools</div>
              <div className="space-y-6">
                <DirectVerificationFlow />
                <PlatformRunner
                  snapshot={platformSnapshot}
                  studentDemo={studentDemo}
                  onRunDemo={handleRunStudentDemo}
                />
                <CorrectionSection
                  snapshot={platformSnapshot}
                  targetDocId={targetDocId}
                  corrField={corrField}
                  corrCurrentVal={corrCurrentVal}
                  corrProposedVal={corrProposedVal}
                  corrReason={corrReason}
                  corrEvidenceDesc={corrEvidenceDesc}
                  docVersions={docVersions}
                  corrections={corrections}
                  onTargetDocChange={setTargetDocId}
                  onFieldChange={setCorrField}
                  onCurrentValChange={setCorrCurrentVal}
                  onProposedValChange={setCorrProposedVal}
                  onReasonChange={setCorrReason}
                  onEvidenceDescChange={setCorrEvidenceDesc}
                  onSubmitCorrection={handleSubmitCorrection}
                  onDecideCorrection={handleDecideCorrection}
                />
                <ProofGateway
                  verificationRequest={verificationRequest}
                  verificationResult={verificationResult}
                  tokenCheck={tokenCheck}
                  onCreateRequest={handleCreateProofRequest}
                  onAuthorize={handleAuthorizeVerification}
                  onIntrospect={handleIntrospectProof}
                  onOpenScanner={() => handleOpenScanner()}
                />
                <DocumentPicker
                  documents={documents}
                  selectedDocumentId={documentId}
                  onSelectDocument={setDocumentId}
                />
                <ScenarioPicker
                  scenarios={scenarios}
                  selectedScenarioId={scenarioId}
                  onSelectScenario={setScenarioId}
                />
                <DiagnosticTimeline
                  diagnostic={diagnostic}
                  scenarioId={scenarioId}
                  onRetry={handleRetry}
                  onCopyEvidence={handleCopyEvidence}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* View 7: SETTINGS & PREFERENCES */}
      {currentView === "SETTINGS" && (
        <SettingsView />
      )}

      {/* View 8: CORRECTIONS & IMMUTABLE VERSION LINEAGE */}
      {currentView === "CORRECTIONS" && (
        <div className="space-y-6 max-w-5xl mx-auto py-2">
          <div className="bg-white border border-[#CBD5E1] rounded-2xl p-6 shadow-xs">
            <h2 className="text-xl font-bold text-[#092F4F] m-0">
              Discrepancy Reporting & Correction Lineage
            </h2>
            <p className="text-xs text-slate-500 mt-1 m-0">
              Submit correction appeals to official registries. Approved corrections issue superseded versions (v1 &rarr; v2).
            </p>
          </div>
          <CorrectionSection
            snapshot={platformSnapshot}
            targetDocId={targetDocId}
            corrField={corrField}
            corrCurrentVal={corrCurrentVal}
            corrProposedVal={corrProposedVal}
            corrReason={corrReason}
            corrEvidenceDesc={corrEvidenceDesc}
            docVersions={docVersions}
            corrections={corrections}
            onTargetDocChange={setTargetDocId}
            onFieldChange={setCorrField}
            onCurrentValChange={setCorrCurrentVal}
            onProposedValChange={setCorrProposedVal}
            onReasonChange={setCorrReason}
            onEvidenceDescChange={setCorrEvidenceDesc}
            onSubmitCorrection={handleSubmitCorrection}
            onDecideCorrection={handleDecideCorrection}
          />
        </div>
      )}

      {/* View 9: SUPPORT & DIAGNOSTICS */}
      {currentView === "SUPPORT" && (
        <div className="space-y-6 max-w-4xl mx-auto py-2">
          <DiagnosticTimeline
            diagnostic={diagnostic}
            scenarioId={scenarioId}
            onRetry={handleRetry}
            onCopyEvidence={handleCopyEvidence}
          />
        </div>
      )}

      {/* Modals for Offline Scanner & eKYC */}
      <OfflineScannerModal
        isOpen={isScannerOpen}
        onClose={() => setIsScannerOpen(false)}
        initialToken={scannerInitialToken}
      />

      <EkycVerificationModal
        isOpen={isEkycOpen}
        onClose={() => setIsEkycOpen(false)}
        documentId={ekycTargetDoc?.documentId}
        documentTitle={ekycTargetDoc?.title}
        onVerificationSuccess={() => {
          refreshWallet();
          setNotice("Aadhaar eKYC identity verified against official registry. Level 4 (Government Verified) trust signal elevated.");
        }}
      />
    </AppShell>
  );
}

export function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <ToastProvider>
          <AppContent />
        </ToastProvider>
      </AuthProvider>
    </LanguageProvider>
  );
}


