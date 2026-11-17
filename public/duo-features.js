const $ = id => document.getElementById(id);
const api = (...args) => {
  if (!window.duoApi) throw new Error('API ещё не инициализирован');
  return window.duoApi(...args);
};
const escapeHTML = (v='') => String(v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const dateInMinsk = value => new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Minsk',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(value));
const todayMinsk = () => dateInMinsk(new Date());
const localMidnight = date => new Date(date+'T00:00:00+03:00');
const fmtDate = date => new Intl.DateTimeFormat('ru-RU',{timeZone:'Europe/Minsk',weekday:'short',day:'numeric',month:'long'}).format(new Date(date));
const fmtTime = date => new Intl.DateTimeFormat('ru-RU',{timeZone:'Europe/Minsk',hour:'2-digit',minute:'2-digit'}).format(new Date(date));
const fmtMoney = n => Number(n).toLocaleString('ru-RU',{maximumFractionDigits:0})+' BYN';
let allEvents=[],rangeMode='7',selectedPlan=null,plansChannel=null;

function initDates(){
  const today=todayMinsk();
  $('planDate').value=today;$('eventsDate').value='';$('eventsDate').min=today;$('planDate').min=today;
}
function eventOnDate(event,day){
  const startDay=dateInMinsk(event.starts_at),endDay=event.ends_at?dateInMinsk(event.ends_at):startDay;
  return Boolean(day)&&day>=startDay&&day<=endDay;
}
function inRange(event,mode){
  const today=todayMinsk(),endDay=event.ends_at?dateInMinsk(event.ends_at):dateInMinsk(event.starts_at);
  if(mode==='all')return endDay>=today;
  if(mode==='date')return eventOnDate(event,$('eventsDate').value);
  const start=localMidnight(today).getTime();
  let from=start,to=start+(Number(mode)||7)*86400000;
  if(mode==='weekend'){const wd=new Date(today+'T12:00:00+03:00').getUTCDay(),toSat=(6-wd+7)%7;from=start+toSat*86400000;to=from+2*86400000}
  const eventStart=new Date(event.starts_at).getTime(),eventEnd=new Date(event.ends_at||event.starts_at).getTime();
  return eventStart<to&&eventEnd>=from;
}
function eventPrice(event){
  if(event.price_min==null)return 'Цена уточняется';
  return 'от '+fmtMoney(event.price_min);
}
function eventDateLabel(event){
  const startDay=dateInMinsk(event.starts_at),endDay=event.ends_at?dateInMinsk(event.ends_at):startDay;
  if(endDay>startDay){
    if(startDay<todayMinsk())return 'До '+fmtDate(event.ends_at);
    return 'С '+fmtDate(event.starts_at)+' · до '+fmtDate(event.ends_at);
  }
  return fmtDate(event.starts_at)+' · '+fmtTime(event.starts_at);
}
function renderEvents(){
  const list=allEvents.filter(event=>event.status==='scheduled'&&inRange(event,rangeMode)).sort((a,b)=>new Date(a.starts_at)-new Date(b.starts_at));
  $('eventsStatus').textContent=list.length?'Найдено событий: '+list.length+' · данные из афиш и билетных площадок':'На эти даты пока нет опубликованных событий. Ниже можно выбрать постоянное место и собрать план без привязки к афише.';
  $('eventsGrid').innerHTML=list.map((event,i)=>{
    const url=event.ticket_url||event.source_url;
    return '<article class="event-card" data-url="'+escapeHTML(url)+'" role="link" tabindex="0" aria-label="Открыть событие '+escapeHTML(event.title)+'" style="animation-delay:'+Math.min(i*35,350)+'ms"><div class="event-date">'+escapeHTML(eventDateLabel(event))+'</div><h3>'+escapeHTML(event.title)+'</h3><div class="event-meta">'+escapeHTML(event.category)+' · '+escapeHTML(event.venue||'Минск')+(event.address?' · '+escapeHTML(event.address):'')+'</div><div class="event-bottom"><span class="event-price">'+escapeHTML(eventPrice(event))+'</span><a class="event-link" href="'+escapeHTML(url)+'" target="_blank" rel="noopener">Подробнее ↗</a></div></article>';
  }).join('');
  const verified=allEvents.reduce((max,event)=>Math.max(max,new Date(event.last_verified_at||0).getTime()),0);
  $('eventsUpdated').textContent=verified?'Последняя проверка: '+new Intl.DateTimeFormat('ru-RU',{timeZone:'Europe/Minsk',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(verified)):'Проверка ещё не выполнялась';
}
async function loadPlaceUpdates(){
  const host=$('placeUpdates');if(!host)return;
  try{
    const data=await api('/updates?limit=9');
    const labels={opened:'Открытие',closed:'Закрылось',temporary_closure:'Временно закрыто',announced_closure:'Объявлено закрытие',reopened:'Снова работает'};
    host.innerHTML=(data||[]).map((item,i)=>{
      const closed=['closed','temporary_closure','announced_closure'].includes(item.change_type);
      const date=new Intl.DateTimeFormat('ru-RU',{day:'numeric',month:'long',year:'numeric'}).format(new Date(item.reported_on+'T12:00:00+03:00'));
      return '<article class="update-card" data-url="'+escapeHTML(item.source_url)+'" role="link" tabindex="0" aria-label="Источник: '+escapeHTML(item.place_name)+'" style="animation-delay:'+Math.min(i*35,300)+'ms"><div class="update-top"><span class="update-tag '+(closed?'closed':'')+'">'+escapeHTML(labels[item.change_type]||'Обновление')+'</span><span class="update-date">Публикация · '+escapeHTML(date)+'</span></div><h3>'+escapeHTML(item.place_name)+'</h3><p>'+escapeHTML(item.description)+'</p>'+(item.address?'<div class="update-address">'+escapeHTML(item.address)+'</div>':'')+'<a class="update-source" href="'+escapeHTML(item.source_url)+'" target="_blank" rel="noopener">Источник: '+escapeHTML(item.source_name)+' ↗</a></article>';
    }).join('')||'<div class="events-status">Пока нет обновлений.</div>';
  }catch(error){host.innerHTML='<div class="events-status">Не удалось загрузить обновления города.</div>';console.error('DUO updates:',error)}
}
async function loadEvents(){
  try{
    allEvents=await api('/events?days=365&limit=500');
    allEvents=(allEvents||[]).filter(event=>new Date(event.ends_at||event.starts_at).getTime()>=Date.now());
    renderEvents();
  }catch(error){$('eventsStatus').textContent='Не удалось загрузить афишу. Постоянные места и генератор свиданий доступны.';console.error('DUO events:',error)}
}
document.querySelectorAll('[data-range]').forEach(button=>button.addEventListener('click',()=>{
  rangeMode=button.dataset.range;
  document.querySelectorAll('[data-range]').forEach(item=>item.classList.toggle('active',item===button));
  $('eventsDate').value='';renderEvents();
}));
$('eventsDate').addEventListener('change',()=>{
  rangeMode=$('eventsDate').value?'date':'7';
  document.querySelectorAll('[data-range]').forEach(item=>item.classList.toggle('active',item.dataset.range==='7'&&rangeMode==='7'));
  renderEvents();
});

const moodCats={
  romantic:['Прогулки и природа','Кафе и рестораны','Музеи и выставки','Кино','SPA и отдых'],
  active:['Игры','Картинг и гонки','Квесты и хоррор','VR и технологии','Скорость','Активити-парки','Лёд'],
  cozy:['Кафе и рестораны','Музеи и выставки','Кино','Прогулки и природа','SPA и отдых','Игры'],
  culture:['Музеи и выставки','Культура','Театр','Кино','Прогулки и природа'],surprise:[]
};
function pickPlaces(mood,budget){
  const places=window.DUO_PLACES||[];
  let pool=places.filter(place=>place.risk!=='avoid'&&place.level<=3&&Number.isFinite(Number(place.cost))&&Number(place.cost)!==999&&Number(place.cost)<=budget);
  const cats=moodCats[mood]||[];
  if(cats.length)pool=pool.filter(place=>cats.some(category=>place.cat.toLowerCase().includes(category.toLowerCase())||category.toLowerCase().includes(place.cat.toLowerCase())));
  if(!pool.length)pool=places.filter(place=>place.risk!=='avoid'&&place.level<=2&&Number(place.cost)===0);
  pool.sort(()=>Math.random()-.5);
  const chosen=[];let left=budget;
  for(const place of pool){const cost=Number(place.cost)||0;if(budget===999||cost<=left){chosen.push(place);if(budget!==999)left-=cost;if(chosen.length===2)break}}
  return chosen;
}
function buildPlan(){
  const date=$('planDate').value||todayMinsk(),mood=$('planMood').value,budget=Number($('planBudget').value);
  const dateEvents=allEvents.filter(event=>eventOnDate(event,date)&&event.status==='scheduled');
  const affordable=dateEvents.filter(event=>event.price_min==null||budget===999||Number(event.price_min)*2<=budget);
  const event=affordable[0]||null;
  const remaining=budget===999?999:Math.max(0,budget-(event?.price_min!=null?Number(event.price_min)*2:0));
  const places=pickPlaces(mood,remaining),steps=[];
  if(event)steps.push({kind:'СОБЫТИЕ',title:event.title,description:(event.venue||'Минск')+' · '+(dateInMinsk(event.starts_at)===date?fmtTime(event.starts_at):'в течение дня')+' · '+eventPrice(event),url:event.ticket_url||event.source_url,event_id:event.id});
  if(places[0])steps.push({kind:event?'ПЕРЕД СОБЫТИЕМ':'ИДЕЯ ВЕЧЕРА',title:places[0].n,description:places[0].desc+' · '+places[0].price,url:places[0].site,place_name:places[0].n});
  if(places[1])steps.push({kind:'ПОСЛЕ',title:places[1].n,description:places[1].desc+' · '+places[1].price,url:places[1].site,place_name:places[1].n});
  if(!steps.length)steps.push({kind:'ПРОГУЛКА',title:'Прогулка по центру Минска',description:'Начните с Троицкого предместья и продолжите вечер в кафе на ваш вкус.',url:'https://www.google.com/maps/search/?api=1&query=Троицкое+предместье+Минск'});
  const moodName={romantic:'Романтичный вечер',active:'Активное свидание',cozy:'Спокойный вечер',culture:'Культурный маршрут',surprise:'Свидание-сюрприз'}[mood];
  const total=steps.reduce((sum,step)=>sum+(step.event_id?(event?.price_min?Number(event.price_min)*2:0):(places.find(place=>place.n===step.place_name)?.cost||0)),0);
  selectedPlan={plan_date:date,title:moodName,mood,budget,items:steps};
  $('planResult').innerHTML='<div class="plan-card"><div class="plan-card-head"><div><div class="eyebrow">ВАШ ПЛАН · '+escapeHTML(fmtDate(localMidnight(date)))+'</div><h3>'+escapeHTML(moodName)+'</h3><div class="plan-card-sub">На двоих · бюджет до '+(budget===999?'без ограничений':fmtMoney(budget))+(budget===999?'':' · ориентир '+fmtMoney(total)+(event&&event.price_min==null?' + цена события уточняется':''))+'</div></div><span class="section-mark">DUO / '+steps.length+' ШАГА</span></div><div class="plan-steps">'+steps.map(step=>'<div class="plan-step"><small>'+escapeHTML(step.kind)+'</small><strong>'+escapeHTML(step.title)+'</strong><p>'+escapeHTML(step.description)+'</p>'+(step.url?'<a href="'+escapeHTML(step.url)+'" target="_blank" rel="noopener">Открыть ↗</a>':'')+'</div>').join('')+'</div><div class="plan-actions"><button class="primary" id="savePlan">Сохранить для нашей пары</button><button id="rerollPlan">Другой вариант ↻</button></div></div>';
  $('savePlan').addEventListener('click',savePlan);$('rerollPlan').addEventListener('click',buildPlan);
}
async function savePlan(){
  if(!selectedPlan)return;
  try{
    await api('/plans',{method:'POST',body:selectedPlan});
    const button=$('savePlan');button.textContent='Сохранено ✓';button.disabled=true;loadSavedPlans();
  }catch(error){
    if(error.message.includes('авторизац')||error.message.includes('сессия')||error.message.includes('пару'))$('accountButton')?.click();
    $('eventsStatus').textContent=error.message;
  }
}
async function loadSavedPlans(){
  const host=$('savedPlans');if(!host)return;
  try{
    const data=await api('/plans');
    const upcoming=(data||[]).filter(plan=>plan.plan_date>=todayMinsk()).slice(0,5);
    if(!upcoming.length){host.innerHTML='';return}
    host.innerHTML='<h4>СОХРАНЁННЫЕ ПЛАНЫ</h4>'+upcoming.map(plan=>'<div class="saved-plan-item"><strong>'+escapeHTML(plan.title)+'</strong><span>'+escapeHTML(plan.plan_date)+' · до '+(Number(plan.budget)>=999?'без ограничений':fmtMoney(plan.budget))+'</span></div>').join('');
  }catch(error){host.innerHTML='';}
}
for(const id of ['eventsGrid','placeUpdates']){
  const host=$(id);
  host?.addEventListener('click',event=>{if(event.target.closest('a,button'))return;const card=event.target.closest('[data-url]');if(card?.dataset.url)window.open(card.dataset.url,'_blank','noopener')});
  host?.addEventListener('keydown',event=>{if(event.key!=='Enter'&&event.key!==' ')return;const card=event.target.closest('[data-url]');if(card){event.preventDefault();window.open(card.dataset.url,'_blank','noopener')}});
}
$('generatePlan').addEventListener('click',buildPlan);
initDates();loadEvents();loadPlaceUpdates();loadSavedPlans();
async function subscribePlansRealtime(){
  const client=window.duoSupabaseRealtime;
  if(!client)return;
  const {data:{session}}=await client.auth.getSession();
  if(!session)return;
  if(plansChannel)await client.removeChannel(plansChannel);
  plansChannel=client.channel('duo-date-plans-'+session.user.id)
    .on('postgres_changes',{event:'*',schema:'public',table:'duo_date_plans'},()=>loadSavedPlans())
    .subscribe();
}
window.duoSupabaseRealtime?.auth.onAuthStateChange(()=>{loadSavedPlans();subscribePlansRealtime()});
subscribePlansRealtime();
