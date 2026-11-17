const fs=require('fs'),p='/Users/yura/Desktop/minsk-auth.js';let s=fs.readFileSync(p,'utf8');
s=s.replace("hydrating=true;closeAuth();updateHeader();window.location.reload()","closeAuth();updateHeader();window.persistCoupleState?.();if(JSON.stringify(old.favs)!==JSON.stringify([...favs])||JSON.stringify(old.visited)!==JSON.stringify([...visited])||JSON.stringify(old.ratings)!==JSON.stringify(ratings))window.location.reload()");
s=s.replace("if(!user||!couple||hydrating)return;","if(!user||!couple)return;");
s=s.replace("const s=localState(),names=new Set([...s.favs,...s.visited,...Object.keys(s.ratings)]);for(const name of names)","const s=localState(),{data:existing}=await sb.from('place_activity').select('place_name').eq('couple_id',couple.id),names=new Set([...(existing||[]).map(x=>x.place_name),...s.favs,...s.visited,...Object.keys(s.ratings)]);for(const name of names)");
s=s.replace(",hydrating=false","");fs.writeFileSync(p,s);console.log('patched auth sync');
