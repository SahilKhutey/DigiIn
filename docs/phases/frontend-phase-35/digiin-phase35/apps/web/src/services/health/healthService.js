export const getHealth=()=>[
['API Gateway','OPERATIONAL',121],['Verification Service','OPERATIONAL',184],['Proof Service','OPERATIONAL',142],['Notification Service','OPERATIONAL',96],['Webhook Service','OPERATIONAL',117],['Audit Service','OPERATIONAL',88]
].map(([service,status,latency])=>({service,status,latency,lastChecked:new Date().toISOString(),version:'v1.0.0'}));
