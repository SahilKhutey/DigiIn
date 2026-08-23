const listeners = new Map();
export const emit = (event) => (listeners.get(event.type) || []).forEach(fn => fn(event));
export const subscribe = (type, fn) => { if (!listeners.has(type)) listeners.set(type, new Set()); listeners.get(type).add(fn); return () => listeners.get(type)?.delete(fn); };
export const createEvent = (type, payload = {}) => ({ id:`EV-${Date.now()}`, type, timestamp:new Date().toISOString(), requestId:`REQ-${Math.random().toString(36).slice(2,8).toUpperCase()}`, payload });
