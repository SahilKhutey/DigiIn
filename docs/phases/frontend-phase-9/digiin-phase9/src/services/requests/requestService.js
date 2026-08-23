const delay = (ms) => new Promise(r => setTimeout(r, ms));
const requests = new Map();
const seed = [
  { id:'VR-82A91', citizenId:'DIN-7K4P-92M8', purpose:'Admission verification', documents:['Class 10 Certificate','Class 12 Certificate'], validityHours:24, status:'completed', organisation:'ABC University', createdAt:new Date(Date.now()-86400000).toISOString(), completedAt:new Date(Date.now()-82800000).toISOString() },
  { id:'VR-83B12', citizenId:'DIN-19A2-6KQ1', purpose:'Scholarship verification', documents:['Class 12 Certificate'], validityHours:24, status:'awaiting_consent', organisation:'ABC University', createdAt:new Date(Date.now()-3600000).toISOString() },
  { id:'VR-84C22', citizenId:'DIN-91K7-4PZ3', purpose:'Employment verification', documents:['Degree Certificate'], validityHours:24, status:'expired', organisation:'ABC University', createdAt:new Date(Date.now()-3*86400000).toISOString() }
];
seed.forEach(r=>requests.set(r.id,r));
const id=()=>`VR-${Math.random().toString(36).slice(2,7).toUpperCase()}`;
export const requestService = {
  async listRequests(){ await delay(180); return [...requests.values()].sort((a,b)=>new Date(b.createdAt)-new Date(a.createdAt)); },
  async getRequest(requestId){ await delay(120); return requests.get(requestId)||null; },
  async createRequest(input){ await delay(450); const r={...input,id:id(),status:'awaiting_consent',organisation:'ABC University',createdAt:new Date().toISOString(),completedAt:null}; requests.set(r.id,r); return r; },
  async cancelRequest(requestId){ await delay(200); const r=requests.get(requestId); if(!r) return null; r.status='cancelled'; return r; },
  async stats(){ const all=[...requests.values()]; return { total:all.length, verified:all.filter(r=>r.status==='completed').length, pending:all.filter(r=>['awaiting_consent','sent','verifying'].includes(r.status)).length, expired:all.filter(r=>r.status==='expired').length }; }
};
