let items = JSON.parse(localStorage.getItem('digiin.notifications') || 'null') || [
{id:'N-1',type:'VERIFICATION_REQUEST',title:'Verification request',message:'ABC University requested admission verification.',read:false,createdAt:new Date().toISOString()},
{id:'N-2',type:'SECURITY_ALERT',title:'Security activity',message:'A new sign-in was detected.',read:true,createdAt:new Date().toISOString()}
];
const save=()=>localStorage.setItem('digiin.notifications',JSON.stringify(items));
export const listNotifications=()=>items;
export const unreadCount=()=>items.filter(x=>!x.read).length;
export const markRead=(id)=>{items=items.map(x=>x.id===id?{...x,read:true}:x);save();};
export const markAllRead=()=>{items=items.map(x=>({...x,read:true}));save();};
export const addNotification=(n)=>{items=[{id:`N-${Date.now()}`,read:false,createdAt:new Date().toISOString(),...n},...items];save();};
