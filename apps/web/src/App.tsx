import { useEffect, useState } from "react";
import * as api from "./api/client";
import { AppShell } from "./layouts/AppShell";
import { AppView } from "./layouts/GovHeader";
import { LandingView } from "./features/landing/LandingView";
import { CitizenVerificationJourney } from "./features/verification/CitizenVerificationJourney";
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
    trustLabel: "Government issued",
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

  // App Perspective / View: LANDING | JOURNEY | WALLET | VERIFIER | CONSENT
  const [currentView, setCurrentView] = useState<AppView>("LANDING");

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
  const [walletDocuments, setWalletDocuments] = useState<WalletDocument[]>([]);

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
      .catch(() =>
        setNotice("Verification gateway demo is available when the API is running.")
      );
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
      .catch(() => setNotice("The demo request could not be authorised."));
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
      .catch(() => setNotice("The demo proof token could not be checked."));
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
        setPlatformSnapshot(snapshot);
        if (studentDemo) {
          setDocVersions(
            snapshot.versions.filter((v) => v.documentId === studentDemo.document.documentId)
          );
          setCorrections(
            snapshot.corrections.filter((c) => c.documentId === studentDemo.document.documentId)
          );
        }
      })
      .catch(() =>
        setNotice("The full platform demo is available when the API is running.")
      );
  };

  const handleSubmitCorrection = () => {
    if (!targetDocId) {
      setNotice("Please select or generate a document first by running the student demo.");
      return;
    }
    api
      .submitCorrectionRequest(targetDocId, {
        field: corrField,
        currentValue: corrCurrentVal,
        proposedValue: corrProposedVal,
        reason: corrReason,
        evidenceDescription: corrEvidenceDesc,
        evidenceReference: `EVID-${Date.now().toString(36).toUpperCase()}`,
      })
      .then(() => {
        setNotice(`Correction request for '${corrField}' submitted to verifier queue.`);
        refreshSnapshot();
        refreshWallet();
      })
      .catch(() => setNotice("Could not submit correction request."));
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
      .catch(() => setNotice("Could not process correction review decision."));
  };

  return (
    <AppShell
      currentView={currentView}
      onViewChange={setCurrentView}
      onOpenScanner={() => handleOpenScanner()}
      onOpenEkyc={() => handleOpenEkyc()}
    >
      <NoticeBanner notice={notice} />

      {/* View 1: PUBLIC LANDING EXPERIENCE */}
      {currentView === "LANDING" && (
        <LandingView
          onStartJourney={() => setCurrentView("JOURNEY")}
          onOpenWallet={() => setCurrentView("WALLET")}
          onOpenVerifier={() => setCurrentView("VERIFIER")}
          onNavigate={(view) => setCurrentView(view)}
        />
      )}

      {/* Public Sub-Pages */}
      {currentView === "ABOUT" && (
        <AboutView onStartJourney={() => setCurrentView("JOURNEY")} />
      )}

      {currentView === "HOW_IT_WORKS" && (
        <HowItWorksView onStartJourney={() => setCurrentView("JOURNEY")} />
      )}

      {currentView === "FOR_CITIZENS" && (
        <ForCitizensView
          onStartJourney={() => setCurrentView("JOURNEY")}
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
        <ContactView />
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


      {/* View 2: CITIZEN 8-STEP VERIFICATION JOURNEY */}
      {currentView === "JOURNEY" && (
        <CitizenVerificationJourney />
      )}



      {/* View 3: CITIZEN DOCUMENT WALLET & VAULT */}
      {currentView === "WALLET" && (
        <div className="space-y-8">
          <DocumentCenter
            walletDocuments={walletDocuments}
            onSelectForCorrection={handleSelectForCorrection}
            onRefreshWallet={refreshWallet}
            onSwitchToVerifier={() => setCurrentView("VERIFIER")}
            onEkycVerify={handleOpenEkyc}
          />

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
      )}

      {/* View 4: VERIFIER & REQUESTER CONSOLE */}
      {currentView === "VERIFIER" && (
        <VerifierDashboard onRefreshWallet={refreshWallet} />
      )}

      {/* View 5: CONSENT & SOVEREIGN AUDIT DASHBOARD */}
      {currentView === "CONSENT" && (
        <ConsentManagerDashboard onNotice={setNotice} />
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
          setNotice("Aadhaar eKYC identity verified! Document trust level elevated to Level 4 (Government Verified).");
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


