"use client";

import {useEffect, useState} from "react";
import {api} from "../lib/api";

export default function Home() {
  const [email,setEmail] = useState("demo@example.com");
  const [password,setPassword] = useState("password123");
  const [logged,setLogged] = useState(false);
  const [credentials,setCredentials] = useState<any[]>([]);
  const [requests,setRequests] = useState<any[]>([]);
  const [message,setMessage] = useState("");

  async function start() {
    try {
      const data = await api("/auth/register", {
        method:"POST",
        body:JSON.stringify({email,password})
      });
      localStorage.setItem("access_token", data.access_token);
      setLogged(true);
      setMessage("Authenticated");
    } catch {
      try {
        const data = await api("/auth/login", {
          method:"POST",
          body:JSON.stringify({email,password})
        });
        localStorage.setItem("access_token", data.access_token);
        setLogged(true);
        setMessage("Authenticated");
      } catch (e:any) { setMessage(e.message); }
    }
  }

  async function load() {
    try {
      setCredentials(await api("/credentials"));
      setRequests(await api("/verification/requests"));
    } catch (e:any) { setMessage(e.message); }
  }

  async function demoCredential() {
    try {
      await api("/credentials", {
        method:"POST",
        body:JSON.stringify({
          credential_type:"CLASS_XII",
          issuer_id:"MOCK_CBSE",
          holder_name:"Demo Citizen",
          passing_year:2026
        })
      });
      setMessage("Government credential added");
      load();
    } catch(e:any){setMessage(e.message)}
  }

  async function newRequest() {
    try {
      await api("/verification/requests", {
        method:"POST",
        body:JSON.stringify({
          requester_name:"National Examination Authority",
          credential_type:"CLASS_XII",
          purpose:"Examination application"
        })
      });
      setMessage("Verification request created");
      load();
    } catch(e:any){setMessage(e.message)}
  }

  async function consentAndVerify(id:string) {
    try {
      await api(`/verification/requests/${id}/consent`, {
        method:"POST",
        body:JSON.stringify({decision:"GRANT"})
      });
      const result = await api(`/verification/requests/${id}/run`, {method:"POST"});
      setMessage(result.proof_id
        ? `Verified. Proof: ${result.proof_id}`
        : `Verification: ${result.result}`);
      load();
    } catch(e:any){setMessage(e.message)}
  }

  useEffect(()=>{ if(logged) load(); },[logged]);

  return <main className="shell">
    <nav className="nav"><div className="brand">DigiLocker X</div><span>Citizen Verification Platform</span></nav>

    {!logged ? <section className="card">
      <h1>Start the citizen journey</h1>
      <p>Authenticate, manage credentials, give consent and produce verification proofs.</p>
      <div style={{maxWidth:420}}>
        <label>Email</label><input value={email} onChange={e=>setEmail(e.target.value)}/><br/>
        <label>Password</label><input type="password" value={password} onChange={e=>setPassword(e.target.value)}/><br/>
        <button className="primary" onClick={start}>Register / Login</button>
      </div>
      <p>{message}</p>
    </section> : <>
      <section className="card">
        <div className="row">
          <button className="primary" onClick={demoCredential}>Add demo government credential</button>
          <button className="secondary" onClick={newRequest}>Create verification request</button>
        </div>
        <p>{message}</p>
      </section>

      <h2>Credentials</h2>
      <section className="grid">
        {credentials.map(c=><article className="card" key={c.id}>
          <h3>{c.credential_type}</h3>
          <span className="status">✓ {c.status}</span>
          <p>Issuer: {c.issuer_id}</p>
          <p>Passing year: {c.passing_year}</p>
          <p>Verification level: {c.verification_level}</p>
        </article>)}
        {!credentials.length && <article className="card">No credentials yet.</article>}
      </section>

      <h2>Verification requests</h2>
      <section className="grid">
        {requests.map(r=><article className="card" key={r.id}>
          <h3>{r.requester_name}</h3>
          <p>{r.purpose}</p>
          <p>Status: <strong>{r.status}</strong></p>
          {r.status !== "COMPLETED" && r.status !== "DENIED" &&
            <button className="primary" onClick={()=>consentAndVerify(r.id)}>Review → Allow → Verify</button>}
        </article>)}
        {!requests.length && <article className="card">No verification requests.</article>}
      </section>
    </>}
  </main>
}
