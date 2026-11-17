import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const APP_URL = 'https://minsk-date-ideas.vercel.app';
const SUPABASE_URL = 'https://crlbtvktwyijkbiiglpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Wdtfv5freKo6BJXg8ETAVw_0qb9H5cB';
const API_BASE = window.DUO_API_URL || '';
const sb = createClient(SUPABASE_URL, SUPABASE_KEY, {
  auth: { flowType: 'implicit', detectSessionInUrl: true, persistSession: true, autoRefreshToken: true }
});
window.duoSupabaseRealtime = sb;

async function api(path, options = {}) {
  const { data: { session } } = await sb.auth.getSession();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (session?.access_token) headers.Authorization = 'Bearer ' + session.access_token;
  const response = await fetch(API_BASE + '/api' + path, {
    ...options, headers,
    body: options.body && typeof options.body !== 'string' ? JSON.stringify(options.body) : options.body
  });
  if (response.status === 204) return null;
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || payload.message || 'Ошибка API: ' + response.status);
  return payload;
}
window.duoApi = api;
window.dispatchEvent(new Event('duo-api-ready'));

const $ = id => document.getElementById(id);
window.loadDuoPlaces?.();
let user = null, couple = null, authMode = 'login', pendingSync = null, liveChannel = null;
const layer = $('authLayer'), body = $('authBody'), message = $('authMessage');
const localState = () => ({
  favs: JSON.parse(localStorage.getItem('minskDuoFavs') || '[]'),
  visited: JSON.parse(localStorage.getItem('minskDuoVisited') || '[]'),
  ratings: JSON.parse(localStorage.getItem('minskDuoRatings') || '{}')
});
function openAuth(){layer.classList.add('open');layer.setAttribute('aria-hidden','false')}
function closeAuth(){layer.classList.remove('open');layer.setAttribute('aria-hidden','true')}
function say(value){message.textContent=value||''}

function authForm(){
  $('authTitle').textContent = authMode === 'login' ? 'С возвращением.' : 'Начнём вместе.';
  $('authSub').textContent = authMode === 'login'
    ? 'Войдите, чтобы продолжить планировать ваши свидания.'
    : 'Создайте аккаунт. Потом пригласите второго человека по коду пары.';
  body.innerHTML = '<div class="auth-tabs"><button class="'+(authMode==='login'?'active':'')+'" id="tabLogin">Войти</button><button class="'+(authMode==='signup'?'active':'')+'" id="tabSignup">Создать аккаунт</button></div><div class="auth-field"><label>EMAIL</label><input id="authEmail" type="email" autocomplete="email" placeholder="you@example.com"></div><div class="auth-field"><label>ПАРОЛЬ</label><input id="authPassword" type="password" autocomplete="'+(authMode==='login'?'current-password':'new-password')+'" placeholder="Минимум 6 символов"></div><button class="auth-submit" id="authSubmit">'+(authMode==='login'?'Войти в аккаунт':'Создать аккаунт')+'</button>';
  $('tabLogin').onclick=()=>{authMode='login';authForm()};
  $('tabSignup').onclick=()=>{authMode='signup';authForm()};
  $('authSubmit').onclick=async()=>{
    say('');
    const email=$('authEmail').value.trim(), password=$('authPassword').value;
    if(!email||!password){say('Введите email и пароль.');return}
    const button=$('authSubmit');button.disabled=true;button.textContent='Подождите…';
    try{
      const result=authMode==='signup'
        ? await sb.auth.signUp({email,password,options:{emailRedirectTo:APP_URL}})
        : await sb.auth.signInWithPassword({email,password});
      if(result.error)throw result.error;
      if(authMode==='signup'&&!result.data.session){say('Письмо отправлено. Подтвердите email по ссылке, затем вернитесь на сайт и войдите.');return}
      user=result.data.user;await afterLogin();
    }catch(error){say(error.message||'Не удалось выполнить вход.')}
    finally{button.disabled=false;button.textContent=authMode==='login'?'Войти в аккаунт':'Создать аккаунт'}
  };
}

function coupleForm(){
  $('authTitle').textContent='Это уже ваше пространство.';
  $('authSub').textContent='Создайте новую пару и отправьте код второму человеку или введите код приглашения.';
  body.innerHTML='<div class="auth-field"><label>НАЗВАНИЕ ПАРЫ</label><input id="coupleName" placeholder="Например, Юра + Аня" maxlength="48"></div><button class="auth-submit" id="createCouple">Создать наше пространство</button><div style="text-align:center;color:#737b87;font-size:10px;margin:16px 0">ИЛИ ПРИСОЕДИНИТЬСЯ</div><div class="auth-field"><label>КОД ПРИГЛАШЕНИЯ</label><input id="inviteCode" placeholder="8 СИМВОЛОВ" maxlength="8" style="text-transform:uppercase;letter-spacing:.18em"></div><button class="auth-secondary" id="joinCouple">Войти по коду пары</button><button class="auth-secondary" id="signOut">Выйти из аккаунта</button>';
  $('createCouple').onclick=async()=>{try{say('Создаём пространство…');couple=await api('/couples',{method:'POST',body:{name:$('coupleName').value||'Наша пара'}});await hydrate()}catch(error){say(error.message)}};
  $('joinCouple').onclick=async()=>{try{say('Проверяем код…');couple=await api('/couples/join',{method:'POST',body:{invite_code:$('inviteCode').value}});await hydrate()}catch(error){say(error.message)}};
  $('signOut').onclick=async()=>{await sb.auth.signOut();user=null;couple=null;authMode='login';authForm()};
}

async function afterLogin(){
  const profile=await api('/me');
  couple=profile.couple;
  if(couple)await hydrate();else coupleForm();
}

async function hydrate(){
  const rows=await api('/activity');
  const old=localState(), favs=new Set(old.favs), visited=new Set(old.visited), ratings={...old.ratings};
  for(const row of rows||[]){
    if(row.is_favorite)favs.add(row.place_name);else favs.delete(row.place_name);
    if(row.visited_at)visited.add(row.place_name);else visited.delete(row.place_name);
    if(row.rating)ratings[row.place_name]=row.rating;else delete ratings[row.place_name];
  }
  localStorage.setItem('minskDuoFavs',JSON.stringify([...favs]));
  localStorage.setItem('minskDuoVisited',JSON.stringify([...visited]));
  localStorage.setItem('minskDuoRatings',JSON.stringify(ratings));
  closeAuth();updateHeader();startRealtime();
  window.persistCoupleState?.();
  if(JSON.stringify([...old.favs].sort())!==JSON.stringify([...favs].sort()) ||
     JSON.stringify([...old.visited].sort())!==JSON.stringify([...visited].sort()) ||
     JSON.stringify(Object.fromEntries(Object.entries(old.ratings).sort()))!==JSON.stringify(Object.fromEntries(Object.entries(ratings).sort()))) {
    window.location.reload();
  }
}

window.persistCoupleState=()=>{
  if(!user||!couple)return;
  clearTimeout(pendingSync);
  pendingSync=setTimeout(async()=>{
    const state=localState(), places=window.DUO_PLACES||[];
    const items=places.map(place=>({
      place_slug:place.n.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-zа-яё0-9]+/gi,'-').replace(/^-|-$/g,'').slice(0,170),
      is_favorite:state.favs.includes(place.n),
      visited:state.visited.includes(place.n),
      rating:state.ratings[place.n]||null
    }));
    try{await api('/activity',{method:'PUT',body:items})}catch(error){console.error('DUO API activity sync:',error)}
  },350);
};

function startRealtime(){
  if(!couple||!sb)return;
  if(liveChannel)sb.removeChannel(liveChannel);
  liveChannel=sb.channel('couple-activity-'+couple.id)
    .on('postgres_changes',{event:'*',schema:'public',table:'place_activity',filter:'couple_id=eq.'+couple.id},async()=>{
      try{
        const rows=await api('/activity'), state=localState();
        const favs=new Set(),visited=new Set(),ratings={};
        for(const row of rows){if(row.is_favorite)favs.add(row.place_name);if(row.visited_at)visited.add(row.place_name);if(row.rating)ratings[row.place_name]=row.rating}
        const changed=JSON.stringify([...favs].sort())!==JSON.stringify([...state.favs].sort())||
          JSON.stringify([...visited].sort())!==JSON.stringify([...state.visited].sort())||
          JSON.stringify(Object.fromEntries(Object.entries(ratings).sort()))!==JSON.stringify(Object.fromEntries(Object.entries(state.ratings).sort()));
        if(changed){localStorage.setItem('minskDuoFavs',JSON.stringify([...favs]));localStorage.setItem('minskDuoVisited',JSON.stringify([...visited]));localStorage.setItem('minskDuoRatings',JSON.stringify(ratings));location.reload()}
      }catch(error){console.error('DUO realtime refresh:',error)}
    }).subscribe();
}

function updateHeader(){
  const button=$('accountButton');if(!button)return;
  button.innerHTML=user?'<i></i><span class="auth-profile">'+(user.email||'Аккаунт')+'</span>':'<i></i><span>Войти / пара</span>';
}

const top=document.querySelector('.topbar'),right=document.createElement('div');
right.className='topbar-right';
right.innerHTML='<button class="auth-trigger" id="accountButton"><i></i><span>Войти / пара</span></button>';
top.appendChild(right);

$('accountButton').onclick=()=>{
  if(user&&couple){
    $('authTitle').textContent='Ваше пространство.';
    $('authSub').textContent='Общие отметки синхронизируются у обоих участников.';
    body.innerHTML='<div class="auth-field"><label>ВАША ПАРА</label><div style="font-size:15px;font-weight:800">'+couple.name+'</div></div><div class="auth-field"><label>КОД ДЛЯ ПРИГЛАШЕНИЯ</label><div class="couple-code">'+couple.invite_code+'</div><button class="auth-secondary" id="copyInvite">Скопировать код</button></div><button class="auth-secondary" id="signOut">Выйти из аккаунта</button>';
    $('copyInvite').onclick=()=>navigator.clipboard.writeText(couple.invite_code).then(()=>say('Код скопирован'));
    $('signOut').onclick=async()=>{await sb.auth.signOut();localStorage.removeItem('minskDuoFavs');localStorage.removeItem('minskDuoVisited');localStorage.removeItem('minskDuoRatings');location.reload()};
  }else if(user)coupleForm();else authForm();
  say('');openAuth();
};
$('authClose').onclick=closeAuth;
layer.addEventListener('click',event=>{if(event.target===layer)closeAuth()});

const {data:{session}}=await sb.auth.getSession();
if(session){user=session.user;try{await afterLogin()}catch(error){authForm();say(error.message);openAuth()}}else authForm();
sb.auth.onAuthStateChange((_event,session)=>{
  if(session?.user&&!user){user=session.user;afterLogin().catch(error=>{say(error.message);openAuth()})}
});
updateHeader();
