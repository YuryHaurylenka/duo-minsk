const fs=require('fs');
const p='/Users/yura/Desktop/Куда сходить в Минске — 100 мест.html';
let h=fs.readFileSync(p,'utf8');
const css=fs.readFileSync('/Users/yura/Desktop/minsk-auth.css.html','utf8');
h=h.replace('function savePersonal(){localStorage.setItem("minskDuoFavs",JSON.stringify([...favs]));localStorage.setItem("minskDuoVisited",JSON.stringify([...visited]));localStorage.setItem("minskDuoRatings",JSON.stringify(myRatings))}','function savePersonal(){localStorage.setItem("minskDuoFavs",JSON.stringify([...favs]));localStorage.setItem("minskDuoVisited",JSON.stringify([...visited]));localStorage.setItem("minskDuoRatings",JSON.stringify(myRatings));window.persistCoupleState?.()}');
h=h.replace('</body>',css+'\n<script type="module" src="/minsk-auth.js"></script>\n</body>');
fs.writeFileSync(p,h);
console.log('patched html',h.length);
