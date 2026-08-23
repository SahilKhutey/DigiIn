const http=require('http');
const routes={
 '/health':()=>({status:'ok',version:'0.11.0'}),
 '/ready':()=>({status:'ready',dependencies:{database:'mock',redis:'mock'}}),
 '/version':()=>({version:'0.11.0',phase:11}),
 '/v1/auth/me':()=>({authenticated:true,user:{digiinId:'DIN-7K4P-92M8'}}),
 '/v1/verification-requests':()=>({requestId:'VR-82A91',status:'awaiting_consent'})
};
http.createServer((req,res)=>{const fn=routes[req.url];res.setHeader('content-type','application/json');if(!fn){res.statusCode=404;return res.end(JSON.stringify({error:{code:'NOT_FOUND',message:'Route not found',requestId:'REQ-DEMO'}}));}res.end(JSON.stringify(fn()));}).listen(3000,()=>console.log('DigiIn Phase 11 API: http://localhost:3000'));
