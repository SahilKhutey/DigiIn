const citizen = { id:'DIN-84K2-19Q7', status:'active', identityStatus:'verified', createdAt:'2026-08-23T10:00:00+05:30' };
const organisation = { id:'ORG-84K2-19Q7', name:'ABC University', type:'Educational institution', status:'active', trustStatus:'verified' };
export const identityService = { async getCitizen(){ return {...citizen}; }, async getOrganisation(){ return {...organisation}; } };
