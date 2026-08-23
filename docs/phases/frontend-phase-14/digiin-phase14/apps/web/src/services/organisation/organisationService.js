const delay = (ms) => new Promise(r => setTimeout(r, ms));
const org = { id:'ORG-84K2-19Q7', name:'ABC University', type:'Educational institution', verified:true, email:'verification@abcuniversity.example', status:'active' };
export const organisationService = {
  async signIn(identifier='ORG-84K2-19Q7'){ await delay(350); return { ...org, sessionId:'org-session-demo' }; },
  async getOrganisation(){ await delay(120); return org; }
};
