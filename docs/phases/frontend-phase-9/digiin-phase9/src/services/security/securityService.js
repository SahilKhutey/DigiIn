const sessions=[{id:'SES-1',device:'Chrome',platform:'Windows',current:true,lastActive:'Now'},{id:'SES-2',device:'Mobile browser',platform:'Android',current:false,lastActive:'12 minutes ago'}];
export const securityService={async sessions(){return sessions.map(x=>({...x}));},async signOut(id){return {id,status:'signed_out'};}};
