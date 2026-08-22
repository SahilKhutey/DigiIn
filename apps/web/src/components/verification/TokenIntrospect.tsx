import type { TokenCheck } from "../../types";

type TokenIntrospectProps = {
  tokenCheck: TokenCheck | null;
  onOpenJwks?: () => void;
};

export function TokenIntrospect({ tokenCheck, onOpenJwks }: TokenIntrospectProps) {
  if (!tokenCheck) return null;

  return (
    <section
      className={`token-check ${tokenCheck.active ? "valid" : "invalid"}`}
      role="status"
      aria-live="polite"
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "10px" }}>
        <div>
          <strong style={{ fontSize: "1rem" }}>{tokenCheck.status}</strong>
          <p style={{ margin: "4px 0" }}>{tokenCheck.message}</p>
        </div>
        {onOpenJwks && (
          <button
            type="button"
            className="secondary"
            onClick={onOpenJwks}
            style={{
              padding: "4px 10px",
              fontSize: ".75rem",
              margin: 0,
              background: "#fff",
              borderColor: "#0b5d9b",
              color: "#0b5d9b",
            }}
          >
            🔑 Public JWKS Discovery
          </button>
        )}
      </div>

      {tokenCheck.active && (
        <div className="token-crypto-meta" style={{ marginTop: "10px", fontSize: ".8rem" }}>
          <span>
            Offline Verifiable: <strong>RFC 7517 Compliant</strong>
          </span>
          {tokenCheck.audience && (
            <span style={{ marginLeft: "14px" }}>
              Bound Audience: <code>{tokenCheck.audience}</code>
            </span>
          )}
        </div>
      )}
    </section>
  );
}
