let permissions = [
 {id:'PER-82A91', organisation:'ABC University', organisationId:'ORG-84K2-19Q7', requestId:'VR-82A91', purpose:'Admission verification', scope:['Class 10 Certificate','Class 12 Certificate'], status:'granted', grantedAt:'2026-08-23T10:32:00+05:30', expiresAt:'2026-08-24T10:32:00+05:30'}
];
export const permissionService = { async list(){ return permissions.map(x=>({...x,scope:[...x.scope]})); }, async revoke(id){ permissions=permissions.map(x=>x.id===id?{...x,status:'revoked',revokedAt:new Date().toISOString()}:x); return permissions.find(x=>x.id===id); } };
