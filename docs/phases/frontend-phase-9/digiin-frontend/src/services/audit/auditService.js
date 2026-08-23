const events=[
 {id:'AUD-1',type:'PROOF_CREATED',resource:'DIN-PRF-51Q8-X2',time:'23 Aug 2026 10:31'},
 {id:'AUD-2',type:'PERMISSION_GRANTED',resource:'ABC University',time:'23 Aug 2026 10:32'},
 {id:'AUD-3',type:'VERIFICATION_COMPLETED',resource:'DIN-VRF-82A91',time:'23 Aug 2026 10:34'},
 {id:'AUD-4',type:'PROOF_VALIDATED',resource:'DIN-PRF-51Q8-X2',time:'23 Aug 2026 10:42'}
];
export const auditService={async list(){return events.map(x=>({...x}));}};
