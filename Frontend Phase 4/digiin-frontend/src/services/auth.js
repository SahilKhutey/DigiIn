const SESSION_KEY='digiin.auth.session';
const PROFILE_KEY='digiin.auth.profile';
const DEMO_OTP='123456';

const read=(key,fallback=null)=>{try{return JSON.parse(localStorage.getItem(key))??fallback}catch{return fallback}};
const write=(key,value)=>localStorage.setItem(key,JSON.stringify(value));

export const authService={
  getSession(){return read(SESSION_KEY)},
  getProfile(){return read(PROFILE_KEY)},
  isAuthenticated(){return Boolean(this.getSession())},
  requestOtp(mobile){
    const normalized=mobile.replace(/\D/g,'');
    if(!/^\d{10}$/.test(normalized)) throw new Error('Enter a valid 10-digit mobile number.');
    write('digiin.auth.otp',{mobile:normalized,createdAt:Date.now(),expiresAt:Date.now()+120000});
    return {mobile:normalized,masked:`+91 ${normalized.slice(0,2)}•••••${normalized.slice(-2)}`,demoOtp:DEMO_OTP};
  },
  verifyOtp(code){
    const otp=read('digiin.auth.otp');
    if(!otp) throw new Error('Request a new OTP to continue.');
    if(Date.now()>otp.expiresAt){localStorage.removeItem('digiin.auth.otp');throw new Error('This OTP has expired. Request a new one.');}
    if(code!==DEMO_OTP) throw new Error('The OTP is incorrect. Try again.');
    const profile=this.getProfile();
    const session={mobile:otp.mobile,createdAt:Date.now(),expiresAt:Date.now()+30*60*1000};
    write(SESSION_KEY,session);
    localStorage.removeItem('digiin.auth.otp');
    return {session,needsOnboarding:!profile};
  },
  completeOnboarding(data){
    const session=this.getSession();
    if(!session) throw new Error('Your session has expired. Please sign in again.');
    const profile={name:data.name.trim(),language:data.language||'en',digiInId:data.digiInId||this.generateId(),createdAt:Date.now()};
    write(PROFILE_KEY,profile);
    return profile;
  },
  generateId(){return `DIN-${Math.random().toString(36).slice(2,6).toUpperCase()}-${Math.random().toString(36).slice(2,6).toUpperCase()}`},
  signOut(){localStorage.removeItem(SESSION_KEY);localStorage.removeItem('digiin.auth.otp')},
  refresh(){
    const session=this.getSession();
    if(session && Date.now()>session.expiresAt){this.signOut();return null}
    return session;
  }
};
