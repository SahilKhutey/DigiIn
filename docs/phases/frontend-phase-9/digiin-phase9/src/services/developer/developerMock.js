export const apiContract={version:'v1',endpoints:[
 {method:'POST',path:'/v1/verification-requests',scope:'verification:create',description:'Create a purpose-bound verification request.'},
 {method:'GET',path:'/v1/verification-requests/:id',scope:'verification:read',description:'Read request status and scope.'},
 {method:'GET',path:'/v1/verifications/:id',scope:'verification:read',description:'Read a completed verification result.'},
 {method:'POST',path:'/v1/proofs/validate',scope:'proof:validate',description:'Validate a DigiIn verification proof.'}
]};
